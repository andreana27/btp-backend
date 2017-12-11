# -*- coding: utf-8 -*-
# intente algo como
@request.restful()
def hook():
    response.view = 'generic.' + request.extension
    def GET(connector, botid, **vars):
        def connfind(bot, connector):
            for conn in bot.connectors:
                if conn['type'] == connector:
                    return conn
        def messenger(bot, conn):
            #raise Exception(request.vars)
            if request.vars['hub.verify_token'] == conn['challenge'] and request.vars['hub.mode'] == 'subscribe':
                return request.vars['hub.challenge']
            return 'Error validating token'
        def telegram(bot, conn):
            #raise Exception('Pending Implementation')
            return
        actions = {'messenger': messenger,
                   'telegram': telegram}
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        return actions[connector](bot, conn)
    def POST(connector, botid, **vars):
        def connfind(bot, connector):
            for conn in bot.connectors:
                if conn['type'] == connector:
                    return conn
        def messenger(bot, conn):
            def log_conversation(chat_id, chat_text, bot, type):
                db.conversation.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       ctype = type,
                                       ccontent = chat_text)
            import requests
            def r(envelope):
                uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = conn['token'])
                resu = requests.post(uri, json=envelope)
                return
            def text(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent')
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'])))
            def quick_reply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent')
                qr = []
                send_to = []
                for q in flow_item['quick_replies']:
                    qr.append(dict(content_type = q['content_type'],
                                   title = q['title'],
                                   payload = ''))
                    if q['sendTo']:
                        send_to.append(':'.join([q['title'], str(q['sendTo'])]))
                #save the send_to, "string_match:context_id,..."
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'send_to'),
                                                         storage_owner = chat_id,
                                                         bot_id = bot.id,
                                                         storage_key = 'send_to',
                                                         storage_value = ','.join(send_to))
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'],
                                             quick_replies = qr)))
            def sender_action(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, "<%s>"%(flow_item['sender_action']), bot.id, 'sent')
                return r(dict(recipient = dict(id = chat_id),
                              sender_action = flow_item['sender_action']))
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                log_conversation(chat_id, '<%s>'%(flow_item['action']), bot.id, 'sent')
                if flow_item['action'] == 'return':
                    #find the parent context and set to it
                    if context.parent_context is not None:
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'current_context'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'current_context',
                                                            storage_value = context.parent_context.id)
                    #change the position back to 0
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = 0)
                elif flow_item['action'] == 'repeat':
                    #just change the next position back to 0, thats it.
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = 0)
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end}
            #if request.vars['hub.verify_token'] == conn['token'] and request.vars['hub.mode'] == 'subscribe':
            for entry in request.vars['entry']:
                chat_text = entry['messaging'][0]['message']['text']
                chat_id = entry['messaging'][0]['sender']['id']
                #conversation gets logged
                log_conversation(chat_id, chat_text, bot, 'received')
                #lines to save the bot data was here
                send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                     (db.bot_internal_storage.bot_id == bot.id)&
                     (db.bot_internal_storage.storage_key == 'send_to')).select().first()
                if send_to:
                    send_to = send_to.storage_value
                    if send_to != '':
                        #Evaluate chat_text with send_to
                        for matches in send_to.split(","):
                            match, action = matches.split(":")
                            if chat_text == match:
                                #send_to that context and clear the direction
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(action))
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'flow_position',
                                                                        storage_value = 0)
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                return messenger(bot, conn)
                #we now get the current context for the chatbot
                current_context = db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                default_context = db((db.bot_context.bot_id == bot.id)&(db.bot_context.name == 'default')).select().first()
                if not current_context:
                    current_context = default_context.id
                else:
                    current_context = int(current_context.storage_value)
                context = db((db.bot_context.id == current_context)).select().first()
                #we now run the flow
                flow_position = db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                if flow_position:
                    flow_position = int(flow_position.storage_value)
                else:
                    flow_position = 0
                flow_item = context.context_json[context.name][flow_position]
                #save the answer of the cliente in the bot_storage table
                #checking if the flow item has the "store" property
                if ('store' in flow_item):
                    #required fields are: bot_id, storage_owner, storage_key, storage_value
                    db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.storage_key == flow_item['store']),
                                                    storage_owner = chat_id,
                                                    bot_id = bot.id,
                                                    storage_key = flow_item['store'],
                                                    storage_value = chat_text)
                next_position = flow_position + 1
                #Make it back to 0
                if next_position >= len(context.context_json[context.name]):
                    next_position = 0
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = next_position)
                #THIS CALL CAN CHANGE THE CONTEXT AND POSITION COMPLETELY
                flow[flow_item['type']](chat_id, flow_item,
                                        bot = bot,
                                        flow_position = flow_position,
                                        current_context = current_context,
                                        context = context)
                if flow_item['type'] == 'sender_action':
                    return messenger(bot, conn)
                if flow_item['type'] == 'end':
                    return messenger(bot, conn)
                #for flow_item in context.context_json[context.name]:
                #    flow[flow_item['type']](chat_id, flow_item)
                return
            return 'Error validating token'
        def telegram(bot, conn):
            import requests
            def r(method, envelope):
                uri = 'https://api.telegram.org/bot{key}/{method}'.format(key = conn['token'],
                                                                          method = method)
                requests.post(uri, json=envelope)
                return
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                if flow_item['action'] == 'return':
                    #find the parent context and set to it
                    if context.parent_context is not None:
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'current_context'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'current_context',
                                                            storage_value = context.parent_context.id)
                    #change the position back to 0
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = 0)
                elif flow_item['action'] == 'repeat':
                    #just change the next position back to 0, thats it.
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = 0)
            def text(chat_id, flow_item, **vars):
                keyboard = []
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content']))
            def quick_reply(chat_id, flow_item, bot, **vars):
                keyboard = []
                send_to = []
                for el in flow_item['quick_replies']:
                    keyboard.append(el['title'])
                    if el['sendTo']:
                        send_to.append(':'.join([el['title'], str(el['sendTo'])]))
                #save the send_to, "string_match:context_id,..."
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'send_to'),
                                                         storage_owner = chat_id,
                                                         bot_id = bot.id,
                                                         storage_key = 'send_to',
                                                         storage_value = ','.join(send_to))
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content'],
                                             reply_markup = dict(keyboard = [keyboard], one_time_keyboard = True)))
            def sender_action(chat_id, flow_item, **vars):
                action = flow_item['sender_action']
                if action == 'typing_on':
                    action = 'typing'
                return r('sendChatAction', dict(chat_id = chat_id,
                                                action = action))
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end}
            #raise Exception(vars)
            chat_id = vars['message']['chat']['id']
            chat_text = vars['message']['text']
            send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                         (db.bot_internal_storage.bot_id == bot.id)&
                         (db.bot_internal_storage.storage_key == 'send_to')).select().first()
            if send_to:
                send_to = send_to.storage_value
                if send_to != '':
                    #Evaluate chat_text with send_to
                    for matches in send_to.split(","):
                        match, action = matches.split(":")
                        if chat_text == match:
                            #send_to that context and clear the direction
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(action))
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'flow_position',
                                                                    storage_value = 0)
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                            return telegram(bot, conn)
            #we now get the current context for the chatbot
            current_context = db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'current_context')).select().first()
            default_context = db((db.bot_context.bot_id == bot.id)&(db.bot_context.name == 'default')).select().first()
            if not current_context:
                current_context = default_context.id
            else:
                current_context = int(current_context.storage_value)
            context = db((db.bot_context.id == current_context)).select().first()
            #we now run the flow
            flow_position = db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
            if flow_position:
                flow_position = int(flow_position.storage_value)
            else:
                flow_position = 0
            flow_item = context.context_json[context.name][flow_position]
            next_position = flow_position + 1
            #Make it back to 0
            if next_position >= len(context.context_json[context.name]):
                next_position = 0
            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                    storage_owner = chat_id,
                                                    bot_id = bot.id,
                                                    storage_key = 'flow_position',
                                                    storage_value = next_position)
            #save the answer of the cliente in the bot_storage table
            #checking if the flow item has the "store" property
            if ('store' in flow_item):
                #required fields are: bot_id, storage_owner, storage_key, storage_value
                db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                (db.bot_storage.storage_owner == chat_id)&
                                                (db.bot_storage.storage_key == flow_item['store']),
                                                storage_owner = chat_id,
                                                bot_id = bot.id,
                                                storage_key = flow_item['store'],
                                                storage_value = chat_text)
            #THIS CALL CAN CHANGE THE CONTEXT AND POSITION COMPLETELY
            flow[flow_item['type']](chat_id, flow_item,
                                    bot = bot,
                                    flow_position = flow_position,
                                    current_context = current_context,
                                    context = context)
            if flow_item['type'] == 'sender_action':
                return telegram(bot, conn)
            if flow_item['type'] == 'end':
                return telegram(bot, conn)
            #for flow_item in context.context_json[context.name]:
            #    flow[flow_item['type']](chat_id, flow_item)
            return
        actions = {'messenger': messenger,
                   'telegram': telegram}
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        #loggin the client response

        return actions[connector](bot, conn)
    def PUT(table_name,record_id,**vars):
        return dict()
    return locals()
