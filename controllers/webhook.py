# -*- coding: utf-8 -*-
# intente algo como
@cors_allow
@request.restful()
def hook():
    response.view = 'generic.' + request.extension
    response.headers["Access-Control-Allow-Origin"] = '*'
    response.headers['Access-Control-Max-Age'] = 86400
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
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
        def website(bot, conn):
            provided_token = request.vars['token']
            verification = db(db.website_token.bot_id == bot, db.website_token.token == provided_token).count()
            return dict(verification = verification)
        actions = {'messenger': messenger,
                   'telegram': telegram,
                  'website': website}
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        return actions[connector](bot, conn)
    response.headers["Access-Control-Allow-Origin"] = '*'
    response.headers['Access-Control-Max-Age'] = 86400
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    def POST(connector, botid, **vars):
        def connfind(bot, connector):
            for conn in bot.connectors:
                if conn['type'] == connector:
                    return conn
        def messenger(bot, conn):
            import datetime
            def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'bot'
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.conversation.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       ctype = type,
                                       ccontent = chat_text,
                                       message_date = current_date,
                                       message_time = current_time,
                                       origin = msg_origin,
                                       medium = 'messenger',
                                       content_type = content_type)
            import requests
            def r(envelope):
                uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = conn['token'])
                resu = requests.post(uri, json=envelope)
                return resu
            def text(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'])))
            def attachment(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['url'], bot.id, 'sent','attachment')
                media_type = flow_item['media_type']
                if media_type == 'link':
                    result = dict(recipient = dict(id = chat_id),
                              message = dict(attachment = dict(type = 'template',
                                                               payload = dict(template_type = 'open_graph',
                                                                              elements = [dict(url = flow_item['url'])]))))
                else:
                    media_type = 'image'
                    result = dict(recipient = dict(id = chat_id),
                              message = dict(attachment = dict(type = media_type,
                                                               payload = dict(url = flow_item['url']))))
                import json
                return r(result)
            def smarText(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'])))
            def smartReply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
            def quick_reply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
                log_conversation(chat_id, "<%s>"%(flow_item['sender_action']), bot.id, 'sent','text')
                return r(dict(recipient = dict(id = chat_id),
                              sender_action = flow_item['sender_action']))
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                log_conversation(chat_id, '<%s>'%(flow_item['action']), bot.id, 'sent','text')
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
            def rest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    data[key['in']] = value.storage_value
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = result))
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest': rest,
                    'attachment' : attachment,
                    'smartText': smarText,
                    'smartReply': smartReply}
            #if request.vars['hub.verify_token'] == conn['token'] and request.vars['hub.mode'] == 'subscribe':
            for entry in request.vars['entry']:
                chat_id = entry['messaging'][0]['sender']['id']
                content_type = 'text'
                if ('text' in entry['messaging'][0]['message']):
                    chat_text = entry['messaging'][0]['message']['text']
                else:
                    chat_text = entry['messaging'][0]['message']['attachments'][0]['payload']['url']
                    content_type = 'attachment'
                #try:
                    #chat_text = entry['messaging'][0]['message']['text']
                #except:
                    #import traceback
                    #chat_text = traceback.format_exc()
                    #chat_text = entry['messaging'][0]['message']['attachments'][0]['payload']['url']
                    #text(chat_id, dict(content = chat_text), bot)
                    #return

                #lines to save the bot data was here
                send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                     (db.bot_internal_storage.bot_id == bot.id)&
                     (db.bot_internal_storage.storage_key == 'send_to')).select().first()
                should_store = db((db.bot_internal_storage.storage_owner == chat_id)&
                             (db.bot_internal_storage.bot_id == bot.id)&
                             (db.bot_internal_storage.storage_key == 'should_store')).select().first()
                #conversation gets logged
                log_conversation(chat_id, chat_text, bot, 'received','attachment')
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
                if should_store:
                    should_store_key = should_store.storage_value
                    db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.storage_key == should_store_key),
                                                    storage_owner = chat_id,
                                                    bot_id = bot.id,
                                                    storage_key = should_store_key,
                                                    storage_value = chat_text)
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                       (db.bot_internal_storage.bot_id == bot.id)&
                       (db.bot_internal_storage.storage_key == 'should_store')).delete()
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
                #SMART OBJECTS
                if flow_position > 0:
                    flow_item_eval = context.context_json[context.name][flow_position - 1]
                    if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                        #Smart response validation request
                        import requests
                        params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                        response = requests.get('http://localhost:5000/parse', params=params)
                        #context = response['intent']
                        #import json
                        json_string = response.json()
                        #getting the conext name
                        context = json_string['intent']['name']
                        if context:
                            context_id = db((db.bot_context.bot_id == bot.id)&
                                     (db.bot_context.name == context)).select(db.bot_context.id).first()
                            if context_id:
                                #send_to that context and clear the direction
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(context_id))
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'flow_position',
                                                                        storage_value = 0)
                                return website(bot, conn)
                #END SMART OBJECTS
                #save the answer of the cliente in the bot_storage table
                #checking if the flow item has the "store" property
                if ('store' in flow_item):
                    #required fields are: bot_id, storage_owner, storage_key, storage_value
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.storage_key == 'should_store'),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             storage_key = 'should_store',
                                                             storage_value = flow_item['store'])
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
            import datetime
            def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'bot'
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.conversation.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       ctype = type,
                                       ccontent = chat_text,
                                       message_date = current_date,
                                       message_time = current_time,
                                       origin = msg_origin,
                                       medium = 'telegram',
                                       content_type = content_type)
            def r(method, envelope):
                uri = 'https://api.telegram.org/bot{key}/{method}'.format(key = conn['token'],
                                                                          method = method)
                retu = requests.post(uri, json=envelope)
                return
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                log_conversation(chat_id, '<%s>'%(flow_item['action']), bot.id, 'sent','text')
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
            def text(chat_id, flow_item, bot,**vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content']))
            def attachment(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['url'], bot.id, 'sent','attachment')
                media_type = flow_item['media_type']
                if media_type == 'link':
                    return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['url']))
                else:
                    media_type = 'image'
                    return r('sendPhoto', dict(chat_id = chat_id,
                                             photo = flow_item['url']))
            def smartText(chat_id, flow_item, bot,**vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = flow_item['content']))
            def smartReply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
            def quick_reply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
            def sender_action(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, "<%s>"%(flow_item['sender_action']), bot.id, 'sent','text')
                action = flow_item['sender_action']
                if action == 'typing_on':
                    action = 'typing'
                return r('sendChatAction', dict(chat_id = chat_id,
                                                action = action))
            def rest(chat_id, flow_item, bot, **vars):
                import requests
                import json
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    data[key['in']] = value.storage_value
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)[:4096]
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)[:4096]
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = result))
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest':rest,
                    'attachment': attachment,
                    'smartText': smartText,
                    'smartReply':smartReply}
            #raise Exception(vars)
            chat_id = vars['message']['chat']['id']
            chat_text = vars['message']['text']
            send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                         (db.bot_internal_storage.bot_id == bot.id)&
                         (db.bot_internal_storage.storage_key == 'send_to')).select().first()
            should_store = db((db.bot_internal_storage.storage_owner == chat_id)&
                             (db.bot_internal_storage.bot_id == bot.id)&
                             (db.bot_internal_storage.storage_key == 'should_store')).select().first()
            #Smart response validation request
            #import httplib, urllib
            #payload = "parse?q=algo&project=default"
            #conn = httplib.HTTPConnection("https://159.89.239:5000")
            #conn.request("POST", "", payload, headers)
            #response = conn.getresponse()
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
            if should_store:
                should_store_key = should_store.storage_value
                db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                (db.bot_storage.storage_owner == chat_id)&
                                                (db.bot_storage.storage_key == should_store_key),
                                                storage_owner = chat_id,
                                                bot_id = bot.id,
                                                storage_key = should_store_key,
                                                storage_value = chat_text)
                db((db.bot_internal_storage.storage_owner == chat_id)&
                   (db.bot_internal_storage.bot_id == bot.id)&
                   (db.bot_internal_storage.storage_key == 'should_store')).delete()
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
            log_conversation(chat_id, chat_text, bot.id, 'received','text')
            #SMART OBJECTS
            if flow_position > 0:
                flow_item_eval = context.context_json[context.name][flow_position - 1]
                if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                    #Smart response validation request
                    import requests
                    params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                    response = requests.get('http://localhost:5000/parse', params=params)
                    #context = response['intent']
                    #import json
                    json_string = response.json()
                    #getting the conext name
                    context = json_string['intent']['name']
                    if context:
                        context_id = db((db.bot_context.bot_id == bot.id)&
                                 (db.bot_context.name == context)).select(db.bot_context.id).first()
                        if context_id:
                            #send_to that context and clear the direction
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(context_id))
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'flow_position',
                                                                    storage_value = 0)
                            return website(bot, conn)
            #END SMART OBJECTS
            #save the answer of the client in the bot_storage table
            #checking if the flow item has the "store" property
            if ('store' in flow_item):
                #required fields are: bot_id, storage_owner, storage_key, storage_value
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.storage_key == 'should_store'),
                                                         storage_owner = chat_id,
                                                         bot_id = bot.id,
                                                         storage_key = 'should_store',
                                                         storage_value = flow_item['store'])
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
            #for flow_item in context.context_json[conteximport requests
            return
        #WEBSITE CHAT WIDGET -------------------------
        #---------------------------------------------
        def website(bot, conn):
            import requests
            import datetime
            def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'bot'
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.conversation.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       ctype = type,
                                       ccontent = chat_text,
                                       message_date = current_date,
                                       message_time = current_time,
                                       origin = msg_origin,
                                       medium = 'website',
                                       content_type = content_type)
            def r(method, envelope):
                return dict(method = method, envelope=envelope)
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                log_conversation(chat_id, '<%s>'%(flow_item['action']), bot.id, 'sent','text')
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
            def text(chat_id, flow_item, bot,**vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                #return dict()
                return r('sendMessage', dict(chat_id = chat_id,text = flow_item['content']))
            def smartText(chat_id, flow_item, bot,**vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                #return dict()
                return r('sendMessage', dict(chat_id = chat_id,text = flow_item['content']))
            def smartReply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
            def quick_reply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
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
            def sender_action(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, "<%s>"%(flow_item['sender_action']), bot.id, 'sent','text')
                action = flow_item['sender_action']
                if action == 'typing_on':
                    action = 'typing'
                return r('sendChatAction', dict(chat_id = chat_id,
                                                action = action))
            def rest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    data[key['in']] = value.storage_value
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = result))
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest': rest,
                    'smartText':smartText,
                    'smartReply':smartReply}
            #raise Exception(vars)
            chat_id = vars['id']
            chat_text = vars['text']
            send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                         (db.bot_internal_storage.bot_id == bot.id)&
                         (db.bot_internal_storage.storage_key == 'send_to')).select().first()
            should_store = db((db.bot_internal_storage.storage_owner == chat_id)&
                              (db.bot_internal_storage.bot_id == bot.id)&
                              (db.bot_internal_storage.storage_key == 'should_store')).select().first()
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
                            return website(bot, conn)
            if should_store:
                should_store_key = should_store.storage_value
                db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                (db.bot_storage.storage_owner == chat_id)&
                                                (db.bot_storage.storage_key == should_store_key),
                                                storage_owner = chat_id,
                                                bot_id = bot.id,
                                                storage_key = should_store_key,
                                                storage_value = chat_text)
                db((db.bot_internal_storage.storage_owner == chat_id)&
                   (db.bot_internal_storage.bot_id == bot.id)&
                   (db.bot_internal_storage.storage_key == 'should_store')).delete()
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
            log_conversation(chat_id, chat_text, bot.id, 'received','text')
            if flow_position > 0:
                flow_item_eval = context.context_json[context.name][flow_position - 1]
                if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                    #Smart response validation request
                    import requests
                    params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                    response = requests.get('http://localhost:5000/parse', params=params)
                    #context = response['intent']
                    #import json
                    json_string = response.json()
                    #getting the conext name
                    context = json_string['intent']['name']
                    if context:
                        context_id = db((db.bot_context.bot_id == bot.id)&
                                 (db.bot_context.name == context)).select(db.bot_context.id).first()
                        if context_id:
                            #send_to that context and clear the direction
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(context_id))
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'flow_position',
                                                                    storage_value = 0)
                            return website(bot, conn)
            #save the answer of the client in the bot_storage table
            #checking if the flow item has the "store" property
            if ('store' in flow_item):
                #required fields are: bot_id, storage_owner, storage_key, storage_value
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.storage_key == 'should_store'),
                                                         storage_owner = chat_id,
                                                         bot_id = bot.id,
                                                         storage_key = 'should_store',
                                                         storage_value = flow_item['store'])
            #THIS CALL CAN CHANGE THE CONTEXT AND POSITION COMPLETELY
            ret = flow[flow_item['type']](chat_id, flow_item,
                                           bot = bot,
                                           flow_position = flow_position,
                                           current_context = current_context,
                                           context = context)
            if flow_item['type'] == 'sender_action':
                return website(bot, conn)
            if flow_item['type'] == 'end':
                return website(bot, conn)
            #if flow_item['type'] == 'rest':
            #    return website(bot, conn)
            #for flow_item in context.context_json[context.name]:
            #    flow[flow_item['type']](chat_id, flow_item)return
            return ret
        #---------------------------------------------
        #END WEBSITE CHAT WIDGET ---------------------
        actions = {'messenger': messenger,
                   'telegram': telegram,
                  'website': website,
                  }
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        #loggin the client response
        return actions[connector](bot, conn)
    return locals()
