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
        def fb(bot, conn):
            raise Exception('Pending Implementation')
            if vars['query']['hub.verify_token'] == conn.token:
                return vars.hub.challenge
            return 'Error validating token'
        def telegram(bot, conn):
            #raise Exception('Pending Implementation')
            return
        actions = {'fb': fb,
                   'telegram': telegram}
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        return actions[connector](bot, conn)
    def POST(connector, botid, **vars):
        def connfind(bot, connector):
            for conn in bot.connectors:
                if conn['type'] == connector:
                    return conn
        def fb(bot, conn):
            raise Exception('Pending Implementation')
            if vars['query']['hub.verify_token'] == conn.token:
                return vars.hub.challenge
            return 'Error validating token'
        def telegram(bot, conn):
            import requests
            def r(method, envelope):
                uri = 'https://api.telegram.org/bot{key}/{method}'.format(key = conn['token'],
                                                                          method = method)
                requests.post(uri, json=envelope)
                return
            def text(chat_id, flow_item):
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content']))
            def quick_reply(chat_id, flow_item):
                keyboard = []
                for el in flow_item['quick_replies']:
                    keyboard.append(el['title'])
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content'],
                                             reply_markup = dict(keyboard = [keyboard])))
            def sender_action(chat_id, flow_item):
                action = flow_item['sender_action']
                if action == 'typing_on':
                    action = 'typing'
                return r('sendChatAction', dict(chat_id = chat_id,
                                                action = action))
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action}
            #raise Exception(vars)
            chat_id = vars['message']['chat']['id']
            #we now get the current context for the chatbot
            context = db((db.bot_context.bot_id == bot.id)).select().first()
            #we now run the flow
            flow_position = db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
            if flow_position:
                flow_position = int(flow_position.storage_value)
            else:
                flow_position = 0
            flow_item = context.context_json[context.name][flow_position]
            flow[flow_item['type']](chat_id, flow_item)
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
            if flow_item['type'] == 'sender_action':
                return telegram(bot, conn)
            #for flow_item in context.context_json[context.name]:
            #    flow[flow_item['type']](chat_id, flow_item)
            return
        actions = {'fb': fb,
                   'telegram': telegram}
        bot = db.bot(id = botid)
        conn = connfind(bot, connector)
        return actions[connector](bot, conn)
    def PUT(table_name,record_id,**vars):
        return dict()
    return locals()
