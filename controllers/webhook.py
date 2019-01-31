#*************
# -*- coding: utf-8 -*-*****
# ------------------------------------------------------------
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
    munisPorDepto = [ 17 #/* 01 - Guatemala tiene: */ 17 /* municipios. */,
        , 8 #/* 02 - El Progreso tiene: */ 8 /* municipios. */,
        , 16 #/* 03 - Sacatepéquez tiene: */ 16 /* municipios. */,
        , 16 #/* 04 - Chimaltenango tiene: */ 16 /* municipios. */,
        , 13 #/* 05 - Escuintla tiene: */ 13 /* municipios. */,
        , 14 #/* 06 - Santa Rosa tiene: */ 14 /* municipios. */,
        , 19 #/* 07 - Sololá tiene: */ 19 /* municipios. */,
        , 8 #/* 08 - Totonicapán tiene: */ 8 /* municipios. */,
        , 24 #/* 09 - Quetzaltenango tiene: */ 24 /* municipios. */,
        , 21 #/* 10 - Suchitepéquez tiene: */ 21 /* municipios. */,
        , 9 #/* 11 - Retalhuleu tiene: */ 9 /* municipios. */,
        , 30 #/* 12 - San Marcos tiene: */ 30 /* municipios. */,
        , 32 #/* 13 - Huehuetenango tiene: */ 32 /* municipios. */,
        , 21 #/* 14 - Quiché tiene: */ 21 /* municipios. */,
        , 8 #/* 15 - Baja Verapaz tiene: */ 8 /* municipios. */,
        , 17 #/* 16 - Alta Verapaz tiene: */ 17 /* municipios. */,
        , 14 #/* 17 - Petén tiene: */ 14 /* municipios. */,
        , 5 #/* 18 - Izabal tiene: */ 5 /* municipios. */,
        , 11 #/* 19 - Zacapa tiene: */ 11 /* municipios. */,
        , 11 #/* 20 - Chiquimula tiene: */ 11 /* municipios. */,
        , 7 #/* 21 - Jalapa tiene: */ 7 /* municipios. */,
        , 17] #/* 22 - Jutiapa tiene: */ 17 /* municipios. *

    def POST(connector, botid, **vars):
        def connfind(bot, connector):
            for conn in bot.connectors:
                if conn['type'] == connector:
                    return conn
        def messenger(bot, conn):
            variable=0
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

            #method to return the current context
            def get_current_context(current_chat_id, current_bot_id):
                #debug(chat_id, "c chat id: {}, c bot id: {}".format(current_chat_id, current_bot_id), bot)
                #GET CURRENT CONTEXT SEARCH
                user_current_context = db((db.bot_internal_storage.storage_owner == current_chat_id)&
                                       (db.bot_internal_storage.bot_id == current_bot_id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                #CHECK IF USER CURRENT CONTEXT NOT HAS VALUE
                if not user_current_context:
                    user_current_context = db((db.bot_context.bot_id == current_bot_id)&(db.bot_context.name == 'default')).select().first()
                else:
                    user_current_context = db((db.bot_context.id) == int(user_current_context.storage_value)).select().first()
                #RETURN CURRENT CONTEXT
                #debug(chat_id, "c context: {}".format(str(user_current_context)), bot)
                return user_current_context

            #method to return if captcha intents exist
            def get_captcha_intents(current_chat_id, current_bot_id):
                #GET CURRENT CAPTCHA INTENTS SEARCH
                captcha_intents = db(
                    (db.bot_internal_storage.storage_owner == current_chat_id) &
                    (db.bot_internal_storage.bot_id == current_bot_id) &
                    (db.bot_internal_storage.storage_key == 'captcha_intents')
                ).select().first()
                if not captcha_intents:
                    #RETURN NONE IF CAPTCHA INTENTS NOT EXIST
                    return None
                #RETURN CAPTCHA INTENTS ITEM
                return captcha_intents

            def r(envelope):
                uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = conn['token'])
                #---------------------------------------------------------------------------------
                if envelope.get('message').get('text'):
                    x=envelope.get('message').get('text')
                    if '{'and '}' in x:
                        llavesopen = x.count("{")
                        llavesclose=x.count("}")
                        for i in range(llavesclose):
                            a = x.find("{")
                            b = x.find("}")
                            key=x[(a+1):b]#sin llaves
                            coincidencia=x[a:(b+1)]#con llaves
                            #search string in table: bot_storage
                            get_value=db((db.bot_storage.storage_key == key)&(db.bot_storage.bot_id==bot.id)&(db.bot_storage.storage_owner==chat_id)).select().first()
                            if get_value!= None:
                                #coincidencia
                                if (a!=-1 or b!=-1) and a<b:
                                    x = x.replace(coincidencia, get_value.storage_value)
                                    envelope['message']['text'] = x
                            else:
                                if (a!=-1 or b!=-1) and a<b:
                                    #sin coincidencia
                                    x = x.replace(coincidencia,"")
                                    envelope['message']['text'] = x
                #----------------------------------------------------
                resu = requests.post(uri, json=envelope)
                return resu
            def debug(chat_id, text, bot, **vars):
                if bot.debug_bot == True:
                    return r(dict(recipient = dict(id = chat_id),
                                  message = dict(text = text)))
            def validationText(chat_id, flow_item, bot, **vars):
                keyboard = []
                debug(chat_id,'inciio bloque VT',bot)
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                retrys=0
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                    repet=int(flow_item['retry'])
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                #debug(chat_id,'repeticiones VT %s maxRepet %s'%(retrys,repet),bot)
                #debug(chat_id,'context IFVT  %s'%(flow_item['sendTo']),bot)
                if(retrys<1):
                    position_value=0
                    try:
                        if flow_item['sendTo']!=None:
                            debug(chat_id,'if sendTo',bot)
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(str(flow_item['sendTo'])))
                        else:
                            debug(chat_id,'else sendTo',bot)
                            current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                            flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                            position_value=int(flow_position_.storage_value)
                            #------------------------------------------------------------------------------------------------
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                     bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(str(current_context_.storage_value)))
                    except Exception as e:
                        #------------------------------------------------------------------------------
                        debug(chat_id,'Exception validationText %s'%(e),bot)
                        #----------------------------------------------------------------
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'flow_position',
                                                                    storage_value=position_value)#0
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                    return messenger(bot, conn)
                else:
                    try:
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'retryText'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'retryText',
                                                                    storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
                    except:
                        debug(chat_id,'error VT',bot)
                    #------------------------------------------------------------------------------------------------
                    flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                    #debug(chat_id,'posicion actual %s'%(flow_position_.storage_value),bot)
                    current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                    debug(chat_id,'context actual %s posicion actual %s'%(current_context_.storage_value,flow_position_.storage_value),bot)
                    #-----------------------------------------------------------------------------------------------
                    if retrys==repet or retrys==10000 or flow_item.get('onError') == None:
                        try:
                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                        except:
                            pass
                        db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_.storage_value,
                                                               context_position = int(flow_position_.storage_value)-1)
                        return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['content'])))
                    else:
                        if len(flow_item['onError'])!=0:
                            return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['onError'])))
                        else:
                            return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['content'])))
            def validationReply(chat_id, flow_item, bot, **vars):
                retrys=0
                debug(chat_id,'start ValidationReply',bot)
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                    repet=int(flow_item['retry'])
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                debug(chat_id,'repeticiones VR %s maxRepet %s'%(retrys,repet),bot)
                if(retrys<1):
                    position_value=0
                    debug(chat_id,'if VR',bot)
                    if flow_item['sendTo']!=None:
                        debug(chat_id,'if con sendto',bot)
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(str(flow_item['sendTo'])))
                    else:
                        debug(chat_id,'else sin sendto',bot)
                        current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                        flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                        position_value=int(flow_position_.storage_value)
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(str(current_context_.storage_value)))
                    #---------******************************************************************************---------------------
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'flow_position',
                                                                    storage_value = position_value)#0
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                    return messenger(bot, conn)
                else:
                    debug(chat_id,'else VR %s'%(str(retrys)),bot)
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'retryReply',
                                                            storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
                    #start reply
                    log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                    qr = []
                    send_to = []
                    for q in flow_item['quick_replies']:
                        qr.append(dict(content_type = q['content_type'],
                                       title = q['title'],
                                       payload = ''))
                        if q['sendTo']:
                            send_to.append(':'.join([q['title'], str(q['sendTo'])]))
                    #-------------------------------------------------------------------------------------------
                    #save the send_to, "string_match:context_id,..."
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'send_to'),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             storage_key = 'send_to',
                                                             storage_value = ','.join(send_to))
                    #-------------------------------------------------------------------------------------------
                    flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                    #debug(chat_id,'posicion actual %s'%(flow_position_.storage_value),bot)
                    current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                    debug(chat_id,'context actual VR %s posicion actual %s'%(current_context_.storage_value,flow_position_.storage_value),bot)
                    #-------------------------------------------------------------------------------------------
                    if retrys==repet or retrys==10000 or flow_item.get('onError') == None:
                        debug(chat_id,'primer contenido',bot)
                        try:
                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                        except:
                            pass
                        db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_.storage_value,
                                                               context_position = int(flow_position_.storage_value)-1)
                        return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['content'],quick_replies = qr)))
                    else:
                        if len(flow_item['onError'])!=0:
                            debug(chat_id,'contenido2 on error',bot)
                            return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['onError'],quick_replies = qr)))
                        else:
                            debug(chat_id,'contenido3 content',bot)
                            return r(dict(recipient = dict(id = chat_id),message = dict(text = flow_item['content'],quick_replies = qr)))
            def chatCenter(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                qr = []
                qr.append(dict(content_type = 'text',title = 'Yes',payload = ''))
                qr.append(dict(content_type = 'text',title = 'No',payload = ''))
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'],
                                             quick_replies = qr)))
            def text(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'])))

            #captcha_method
            def captcha(chat_id, flow_item, bot, **vars):
                from captcha.image import ImageCaptcha
                import random
                import string
                import base64
                #path for fonts and images
                fonts_path = '/opt/web2py_apps/web2py.production/applications/backend/static/fonts/captcha_fonts/'
                font_name = fonts_path + 'Nobile-Medium.ttf'
                captcha_images_path = '/opt/web2py_apps/web2py.production/applications/backend/static/images/captcha_images/'
                public_captcha_images_path = 'https://demo-backend.botprotec.com/backend/static/images/captcha_images/'
                #-----Bantrab--------
                #fonts_path = '/opt/web2py_apps/web2py/applications/backend/static/fonts/captcha_fonts/'
                #font_name = fonts_path + 'Nobile-Medium.ttf'
                #captcha_images_path = '/opt/web2py_apps/web2py/applications/backend/static/images/captcha_images/'
                #public_captcha_images_path = 'https://des-backend-chatbot.bantrab.com.gt/backend/static/images/captcha_images/'
                #*****especial para bancredit***********
                #public_captcha_images_path = 'https://backend-bancredit.botprotec.com/backend/static/images/captcha_images/'
                #------------------------------------------------------------------------------------------
                
                #settings
                image = ImageCaptcha(fonts=[font_name])
                #idkw
                log_conversation(chat_id, flow_item['message'], bot.id, 'sent', 'text')
                #bienvenida
                valor = flow_item['value']
                #get validation request
                retry = flow_item['validation']
                #get message if captcha not resolved
                message = flow_item['message']
                #get length captcha generator use for captcha
                length = int(flow_item['length'])
                #create captcha value
                captcha_quest = "".join([random.choice(string.letters) for i in xrange(length)])
                captcha_quest = captcha_quest.lower()
                #create captcha quest route
                captcha_image_route = captcha_images_path + captcha_quest + ".png"
                public_captcha_image_route = public_captcha_images_path + captcha_quest + ".png"
                #generate image
                image_created = image.write(captcha_quest, captcha_image_route)
                db.bot_internal_storage.update_or_insert(
                    (db.bot_internal_storage.storage_owner == chat_id) &
                    (db.bot_internal_storage.bot_id == bot.id) &
                    (db.bot_internal_storage.storage_key == 'captcha_quest'),
                    storage_owner = chat_id,
                    bot_id = bot.id,
                    storage_key = 'captcha_quest',
                    storage_value = captcha_quest
                )
                #----------------------------------------------------------------------------------
                uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = conn['token'])
                params=dict(recipient = dict(id = chat_id),message = dict(text = valor))
                resu = requests.post(uri, json=params)
                debug(chat_id,'response: "%s"' % (resu), bot)
                #-----------------------------------------------------------------------------------
                return r(dict(
                        recipient = dict(id = chat_id),
                        message = dict(
                            attachment = dict(
                                type = 'image',
                                payload = dict(url = str(public_captcha_image_route))
                            )
                        )
                    ))

            #validation count method
            def countValidation(chat_id, flow_item, bot, **vars):

                item_id = 'count_validation_{}'.format(flow_item['id'])
                item_intents = flow_item['limit']
                item_users = flow_item['users']
                item_users_excluded = []
                item_send_to = flow_item['sendTo']
                message = flow_item['message']

                for item_user in item_users:
                    item_users_excluded.append(item_user[0])

                check_intents = db(
                    (db.bot_internal_storage.storage_owner == chat_id) &
                    (db.bot_internal_storage.bot_id == bot.id) &
                    (db.bot_internal_storage.storage_key ==  '{}_intents'.format(item_id))
                ).select(db.bot_internal_storage.storage_value)

                if chat_id in item_users_excluded:
                    return r(dict(recipient = dict(id = chat_id),
                                  message = dict(text = "user excluded")))

                if len(check_intents) == 0:
                    db.bot_internal_storage.insert(
                        storage_owner = chat_id,
                        bot_id = bot.id,
                        storage_key = '{}_intents'.format(item_id),
                        storage_value = 1
                    )
                    #debug(chat_id,'primera vez',bot)
                    #return r(dict(recipient = dict(id = chat_id),
                    #              message = dict(text = "first")))
                    return

                else:
                    #debug(chat_id,'otras veces',bot)

                    intents = db(
                        (db.bot_internal_storage.storage_owner == chat_id) &
                        (db.bot_internal_storage.bot_id == bot.id) &
                        (db.bot_internal_storage.storage_key ==  '{}_intents'.format(item_id))
                    ).select(db.bot_internal_storage.storage_value).first().storage_value

                    if(int(intents) < int(item_intents)):
                        db.bot_internal_storage.update_or_insert(
                            (db.bot_internal_storage.storage_owner == chat_id) &
                            (db.bot_internal_storage.bot_id == bot.id) &
                            (db.bot_internal_storage.storage_key == item_id + '_intents'),
                            storage_value = int(check_intents[0].storage_value) + 1
                        )
                        #return r(dict(recipient = dict(id = chat_id),
                        #          message = dict(text = "pass")))
                        return
                    else:

                        db.bot_internal_storage.update_or_insert(
                            (db.bot_internal_storage.storage_owner == chat_id) &
                            (db.bot_internal_storage.bot_id == bot.id) &
                            (db.bot_internal_storage.storage_key == 'current_context'),
                            storage_owner = chat_id,
                            bot_id = bot.id,
                            storage_key = 'current_context',
                            storage_value = int(item_send_to)
                        )
                        db.bot_internal_storage.update_or_insert(
                            (db.bot_internal_storage.storage_owner == chat_id) &
                            (db.bot_internal_storage.bot_id == bot.id) &
                            (db.bot_internal_storage.storage_key == 'flow_position'),
                            storage_owner = chat_id,
                            bot_id = bot.id,
                            storage_key = 'flow_position',
                            storage_value = 0
                        )
                        return r(dict(recipient = dict(id = chat_id),
                                  message = dict(text = message)))

            def checkPoint(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                import datetime
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.bot_checkpoint.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       checkpoint_date = current_date,
                                       checkpoint_time = current_time,
                                       checkpoint_name = flow_item['content'],
                                       medium = 'messenger')
                return messenger(bot,conn)
            def attachment(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['url'], bot.id, 'sent','attachment')
                media_type = flow_item['media_type']
                if media_type == 'link':
                    result = dict(
                        recipient = dict(id = chat_id),
                        message = dict(
                            attachment = dict(
                                type = 'template',
                                payload = dict(
                                    template_type = 'open_graph',
                                    elements = [dict(url = flow_item['url'])]
                                )
                            )
                        )
                    )
                else:
                    media_type = 'image'
                    result = dict(
                        recipient = dict(id = chat_id),
                        message = dict(
                            attachment = dict(
                                type = media_type,
                                payload = dict(url = flow_item['url'])
                            )
                        )
                    )
                import json
                return r(result)
            def smarText(chat_id, flow_item, bot, **vars):
                debug(chat_id,'inciio bloque ST',bot)
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                try:
                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                except:
                    pass
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
                try:
                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                except:
                    pass
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = flow_item['content'],
                                             quick_replies = qr)))
            def quick_reply(chat_id,flow_item, bot, **vars):
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
                debug(chat_id,'Inicia-End %s'%(flow_item['action']),bot)
                if flow_item['action'] == 'return':
                    #find the parent context and set to it
                    try:
                        db(db.bot_context_heap.bot_id ==bot.id).delete()
                    except:
                        pass
                    next_position_ = 0
                    heap_ = db((db.bot_context_heap.storage_owner == chat_id)&
                               (db.bot_context_heap.bot_id == bot.id)).select(db.bot_context_heap.ALL, orderby=~db.bot_context_heap.id).first()
                    debug(chat_id,'heap_ =%s'%(heap_),bot)
                    if(heap_ is not None):
                        debug(chat_id,'heap_ no es None pos=0',bot)
                        next_position_ = 0
                    else:
                        if context.parent_context is not None:
                            debug(chat_id,'Parent Context es None, context %s pos 0'%(context.parent_context.id),bot)
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
                                                                storage_value = next_position_)
                elif flow_item['action'] == 'repeat':
                    #just change the next position back to 0, thats it.
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = 0)
                #return messenger(bot, conn)
            def rest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    if value:
                        data[key['in']] = value.storage_value
                    else:
                        data[key['in']] = None
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r(dict(recipient = dict(id = chat_id),
                              message = dict(text = result)))
            def decisionRest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    if value:
                        data[key['in']] = value.storage_value
                    else:
                        data[key['in']] = None
                debug(chat_id,'About to try request %s to %s' % (flow_item['method'], flow_item['url']),bot)
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                qr = []
                for q in flow_item['quick_replies']:
                    snd = q['sendTo']
                    val = q['title']
                    debug(chat_id,'Testing %s with %s' % (result, val),bot)
                    if(result==val):
                        debug(chat_id,'Test passed, seting current context: %s and flow_position: %s' % (snd, 0),bot)
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'current_context'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'current_context',
                                                                        storage_value = int(snd))
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                            storage_owner = chat_id,
                                                                            bot_id = bot.id,
                                                                            storage_key = 'flow_position',
                                                                            storage_value = 0)
                debug(chat_id,'About to log conversation',bot)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                debug(chat_id,'Finishing decisionRest',bot)
                return
            #-------------webView elemento-----------------------------------------
            def webView(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                debug(chat_id,'inicio de Webview', bot)
                #------conexion con fb------------------------------------------------
                import requests
                #-------------------------------------------------------------------
                idbot=str(int(bot.id))
                iduser=str(int(chat_id))
                uri_mod=flow_item['url']+"?bot="+idbot+"&psid="+iduser
                #-------------------------------------------------------------------
                params = dict(recipient = dict(id = iduser),
                              message = dict(attachment = dict(type = "template", 
                                                               payload = dict(template_type = "button",
                                                                              text = flow_item['content'],
                                                                              buttons = [dict(type = "web_url",
                                                                                              url = uri_mod,
                                                                                              title = flow_item['button'],
                                                                                              webview_share_button = "hide",
                                                                                              messenger_extensions = "true",
                                                                                              fallback_url = uri_mod,
                                                                                              webview_height_ratio = "tall")]))))
                uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = conn['token'])
                resu = requests.post(uri, json=params)
                debug(chat_id,'final: "%s"' % (resu), bot)
                return #r(dict(recipient = dict(id = chat_id)))
            #---------------------------------------------------------------------------
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest': rest,
                    'attachment' : attachment,
                    'smartText': smarText,
                    'chatCenter':chatCenter,
                    'validationText':validationText,
                    'validationReply':validationReply,
                    'checkPoint':checkPoint,
                    'decisionRest':decisionRest,
                    'smartReply': smartReply,
                    'captcha': captcha,
                    'countValidation': countValidation,
                    'webView':webView
                   }
            #if request.vars['hub.verify_token'] == conn['token'] and request.vars['hub.mode'] == 'subscribe':
            import json
            json_envelope = json.dumps(request.vars)
            for entry in request.vars['entry']:
                import json
                import os
                chat_id = entry['messaging'][0]['sender']['id']
                #----------------------------------------------------
                content_type = 'text'
                #flujo normal
                if entry['messaging'][0].get('message'):
                    #---------------------------------------------------------------------------------
                    req = requests.get('https://graph.facebook.com/'+chat_id+'?fields=name,first_name,last_name,profile_pic&access_token='+conn['token'])
                    jsonstring = req.json()
                    username_fb=jsonstring['name']
                    first_name=jsonstring['first_name']
                    last_name=jsonstring['last_name']
                    profile_pic=jsonstring['profile_pic']
                    #try:
                    db.bot_storage.update_or_insert((db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_key =='fb_username'),
                                                  storage_owner = chat_id,
                                                  bot_id = bot.id,
                                                  storage_key='fb_username',
                                                  storage_value=username_fb)
                    db.commit()
                    db.bot_storage.update_or_insert((db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_key =='fb_profile_pic'),
                                                    storage_owner = chat_id,
                                                  bot_id = bot.id,
                                                  storage_key='fb_profile_pic',
                                                  storage_value=profile_pic)
                    db.commit()
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id),
                                                                 storage_owner = chat_id,
                                                                 bot_id = bot.id,
                                                                 first_contact=datetime.datetime.now(),
                                                                 fbuser_name=username_fb,
                                                                 first_namefb=first_name,
                                                                 last_namefb=last_name)
                    #except:
                        #pass
                    #---------------------------------------------------------------------------------
                    if ('text' in entry['messaging'][0]['message']):
                        chat_text = entry['messaging'][0]['message']['text']
                        #debug(chat_id,'entrada1: %s'%(chat_text),bot)
                    else:
                        chat_text = entry['messaging'][0]['message']['attachments'][0]['payload']['url']
                        content_type = 'attachment'
                else:
                    #flujo con messaging_referral----------
                    import datetime
                    import requests
                    current_date = datetime.datetime.now()
                    id_user=entry['messaging'][0]['sender']['id']
                    token_bot=conn['token']
                    #-------send id_user a fb--------------------------------------------------
                    req = requests.get('https://graph.facebook.com/'+id_user+'?fields=name,first_name,last_name,profile_pic&access_token='+token_bot)
                    jsonstring = req.json()
                    username_fb=jsonstring['name']
                    first_name=jsonstring['first_name']
                    last_name=jsonstring['last_name']
                    profile_pic=jsonstring['profile_pic']
                    #try:
                    db.bot_storage.update_or_insert((db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_key =='fb_username'),
                                                  storage_owner = chat_id,
                                                  bot_id = bot.id,
                                                  storage_key='fb_username',
                                                  storage_value=username_fb)
                    db.commit()
                    db.bot_storage.update_or_insert((db.bot_storage.storage_owner == chat_id)&
                                                    (db.bot_storage.bot_id == bot.id)&
                                                    (db.bot_storage.storage_key =='fb_profile_pic'),
                                                    storage_owner = chat_id,
                                                  bot_id = bot.id,
                                                  storage_key='fb_profile_pic',
                                                  storage_value=profile_pic)
                    db.commit()
                    #except:
                        #pass
                    #----------------------------------------------------------------------------------
                    if entry['messaging'][0]['postback'].get('referral'):
                        #1 es un anuncio
                        import datetime
                        if entry['messaging'][0]['postback']['referral'].get('ad_id'):
                            ads=entry['messaging'][0]['postback']['referral']['ad_id']
                            reference=entry['messaging'][0]['postback']['referral']['ref']
                            source=entry['messaging'][0]['postback']['referral']['source']
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             channel_id=reference,
                                                             source_type=source,
                                                             ad_id=ads,
                                                             first_contact=datetime.datetime.now(),
                                                             fbuser_name=username_fb,
                                                             first_namefb=first_name,
                                                             last_namefb=last_name)
                            db.commit()
                        else:
                            debug(chat_id,'entro al else',bot)
                            #2 es m.me/codigo de fb/plugin chat
                            if entry['messaging'][0]['postback']['referral'].get('ref') and entry['messaging'][0]['postback']['referral'].get('source'):
                                import datetime
                                reference=entry['messaging'][0]['postback']['referral']['ref']
                                source=entry['messaging'][0]['postback']['referral']['source']
                                debug(chat_id,'Else    ref:-- %s source:-- %s'%(reference,source),bot)
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             channel_id=reference,
                                                             source_type=source,
                                                             first_contact=datetime.datetime.now(),
                                                             fbuser_name=username_fb,
                                                             first_namefb=first_name,
                                                             last_namefb=last_name)
                                db.commit()
                                #3 es pestana sugerencia
                            elif entry['messaging'][0]['postback']['referral'].get('source'):
                                import datetime
                                source=entry['messaging'][0]['postback']['referral']['source']
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             source_type=source,
                                                             first_contact=datetime.datetime.now(),
                                                             fbuser_name=username_fb,
                                                             first_namefb=first_name,
                                                             last_namefb=last_name)
                                db.commit()
                            else:
                                pass
                    else:
                        #4 no tiene ref
                        import datetime
                        debug(chat_id,'no tiene parametros fecha: %s',bot)
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id),
                                                             storage_owner = chat_id,
                                                             bot_id = bot.id,
                                                             channel_id='Otros',
                                                             first_contact=datetime.datetime.now(),
                                                             fbuser_name=username_fb,
                                                             first_namefb=first_name,
                                                             last_namefb=last_name)
                        db.commit()
                    #------------------------------------------------------------------
                debug(chat_id,
                      'Facebook Message: "%s"' % (json.dumps(entry)), bot)
                if chat_text:
                    if type(chat_text) != unicode:
                        chat_text = unicode(chat_text,'utf-8')
                debug(chat_id,
                      'Received message: "%s", bot id "%s", chat_id "%s", envelope "%s"' % (chat_text,
                                                                                            bot.id,
                                                                                            chat_id,
                                                                                            json_envelope),
                      bot)
                resp=db((db.conversation.bot_id==bot.id)&(db.conversation.storage_owner==chat_id))
                needchat=False
                 #check if bot is available
                available = db(db.bot.id == bot.id).select().first().enabled
                #kill bot flow if not available
                if not available:
                    return None
                #check chat center
                try:
                    needchat=resp.select(db.conversation.need_chat_center)[0]['need_chat_center']
                except:
                    needchat=False
                if(needchat):
                    def log_conversationtrue(chat_id, chat_text, bot, type,content_type):
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
                                       content_type = content_type,
                                       need_chat_center=True)
                    log_conversationtrue(chat_id, chat_text, bot, 'received','text')
                    debug(chat_id, 'Logged message: "%s"' % (chat_text), bot)
                    return 0
                #try:
                    #chat_text = entry['messaging'][0]['message']['text']
                #except:
                    #import traceback
                    #chat_text = traceback.format_exc()
                    #chat_text = entry['messaging'][0]['message']['attachments'][0]['payload']['url']
                    #text(chat_id, dict(content = chat_text), bot)
                    #return

                #Captcha test analize
                #captcha_validate_values
                item_flow_position = db(
                    (db.bot_internal_storage.storage_owner == chat_id) &
                    (db.bot_internal_storage.bot_id == bot.id) &
                    (db.bot_internal_storage.storage_key == 'flow_position')
                ).select()

                if item_flow_position:
                    item_flow_position = item_flow_position.first().storage_value

                    context_to_eval = get_current_context(chat_id, bot.id)
                    item_to_eval = context_to_eval.context_json[context_to_eval.name][int(item_flow_position) - 1]
                    if item_to_eval['type'] == 'captcha':
                        possible_captcha = db(
                            (db.bot_internal_storage.storage_owner == chat_id) &
                            (db.bot_internal_storage.bot_id == bot.id) &
                            (db.bot_internal_storage.storage_key ==  'captcha_quest')
                        ).select()
                        if len(possible_captcha) > 0:
                            possible_captcha = possible_captcha.first()
                        else:
                            possible_captcha = None
                        if possible_captcha:
                            value_to_compare = possible_captcha.storage_value
                            image_route = "/opt/web2py_apps/web2py.production/applications/backend/static/images/captcha_images/{}.png".format(possible_captcha.storage_value)
                            try:
                                os.remove(image_route)
                            except:
                                pass
                            db(
                                (db.bot_internal_storage.storage_owner == chat_id) &
                                (db.bot_internal_storage.bot_id == bot.id) &
                                (db.bot_internal_storage.storage_key ==  'captcha_quest')
                            ).delete()

                            flow_position = db(
                                (db.bot_internal_storage.storage_owner == chat_id) &
                                (db.bot_internal_storage.bot_id == bot.id) &
                                (db.bot_internal_storage.storage_key == 'flow_position')
                            ).select().first().storage_value

                            if str(chat_text.strip()) == str(value_to_compare):
                                captcha_intents = get_captcha_intents(chat_id, bot.id)
                                if captcha_intents:
                                    db(
                                        (db.bot_internal_storage.storage_owner == chat_id) &
                                        (db.bot_internal_storage.bot_id == bot.id) &
                                        (db.bot_internal_storage.storage_key == 'captcha_intents')
                                    ).delete()
                            else:
                                captcha_current_context = get_current_context(chat_id, bot.id)
                                flow_item = captcha_current_context.context_json[captcha_current_context.name][int(flow_position) - 1]
                                limit = int(flow_item['validation'])
                                captcha_intents = get_captcha_intents(chat_id, bot.id)

                                if not captcha_intents:
                                    db.bot_internal_storage.bulk_insert([{
                                        'storage_owner': chat_id,
                                        'bot_id': bot.id,
                                        'storage_key': 'captcha_intents',
                                        'storage_value': 1
                                    }])

                                    #debug(chat_id,'pos captcha %s'%((int(flow_position) - 1)),bot)
                                    db.bot_internal_storage.update_or_insert(
                                        (db.bot_internal_storage.storage_owner == chat_id) &
                                        (db.bot_internal_storage.bot_id == bot.id) &
                                        (db.bot_internal_storage.storage_key == 'flow_position'),
                                        storage_owner = chat_id,
                                        bot_id = bot.id,
                                        storage_key = 'flow_position',
                                        storage_value = (int(flow_position) - 1)
                                    )
                                    return messenger(bot, conn)

                                elif int(captcha_intents.storage_value) < (int(limit) - 1):
                                    db.bot_internal_storage.update_or_insert(
                                        (db.bot_internal_storage.storage_owner == chat_id) &
                                        (db.bot_internal_storage.bot_id == bot.id) &
                                        (db.bot_internal_storage.storage_key == 'captcha_intents'),
                                        storage_value = int(captcha_intents.storage_value) + 1
                                    )

                                    #debug(chat_id,'pos captcha %s'%((int(flow_position) - 1)),bot)
                                    db.bot_internal_storage.update_or_insert(
                                        (db.bot_internal_storage.storage_owner == chat_id) &
                                        (db.bot_internal_storage.bot_id == bot.id) &
                                        (db.bot_internal_storage.storage_key == 'flow_position'),
                                        storage_owner = chat_id,
                                        bot_id = bot.id,
                                        storage_key = 'flow_position',
                                        storage_value = (int(flow_position) - 1)
                                    )
                                    return messenger(bot, conn)
                                else:
                                    captcha_intents = get_captcha_intents(chat_id, bot.id)

                                    if captcha_intents:
                                        db.bot_internal_storage.update_or_insert(
                                            (db.bot_internal_storage.storage_owner == chat_id) &
                                            (db.bot_internal_storage.bot_id == bot.id) &
                                            (db.bot_internal_storage.storage_key == 'backup_intents'),
                                            storage_owner = chat_id,
                                            bot_id = bot.id,
                                            storage_key = 'backup_intents',
                                            storage_value = int(captcha_intents.storage_value) + 1
                                        )
                                        db(
                                            (db.bot_internal_storage.storage_owner == chat_id) &
                                            (db.bot_internal_storage.bot_id == bot.id) &
                                            (db.bot_internal_storage.storage_key == 'captcha_intents')
                                        ).delete()

                                    db.bot_internal_storage.update_or_insert(
                                        (db.bot_internal_storage.storage_owner == chat_id) &
                                        (db.bot_internal_storage.bot_id == bot.id) &
                                        (db.bot_internal_storage.storage_key == 'flow_position'),
                                        storage_owner = chat_id,
                                        bot_id = bot.id,
                                        storage_key = 'flow_position',
                                        storage_value = 0
                                    )
                                    if captcha_current_context.parent_context:
                                        db.bot_internal_storage.update_or_insert(
                                            (db.bot_internal_storage.storage_owner == chat_id) &
                                            (db.bot_internal_storage.bot_id == bot.id) &
                                            (db.bot_internal_storage.storage_key == 'current_context'),
                                            storage_owner = chat_id,
                                            bot_id = bot.id,
                                            storage_key = 'current_context',
                                            storage_value = int(captcha_current_context.parent_context)
                                        )

                                    return messenger(bot, conn)


                #lines to save the bot data was here
                send_to = db((db.bot_internal_storage.storage_owner == chat_id)&
                     (db.bot_internal_storage.bot_id == bot.id)&
                     (db.bot_internal_storage.storage_key == 'send_to')).select().first()
                should_store = db((db.bot_internal_storage.storage_owner == chat_id)&
                             (db.bot_internal_storage.bot_id == bot.id)&
                             (db.bot_internal_storage.storage_key == 'should_store')).select().first()
                #conversation gets logged
                log_conversation(chat_id, chat_text, bot, 'received','text')
                if send_to:
                    send_to = send_to.storage_value
                    debug(chat_id, 'identified "send_to": "%s"' % (send_to), bot)
                    if send_to != '':
                        #Evaluate chat_text with send_to
                        for matches in send_to.split(","):
                            match, action = matches.split(":")
                            if type(match) != unicode:
                                match = unicode(match, 'utf-8')
                            import unicodedata
                            debug(chat_id, 'testing "chat_text": "%s" with send_to match "%s"' % (chat_text.strip(),
                                                                                                  match.strip()), bot)
                            if chat_text.strip() == match.strip():
                                debug(chat_id,'iguales',bot)
                                flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                debug(chat_id, 'send_to matched, flow_positon is: "%s"' % (flow_position_.storage_value), bot)
                                if(int(flow_position_.storage_value)!=0):
                                    current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                    current_context_id = 0
                                    if(current_context_!=None):
                                        current_context_id = current_context_.storage_value
                                    else:
                                        default_context = db((db.bot_context.bot_id == bot.id)
                                                             &(db.bot_context.name == 'default')).select().first()
                                        current_context_id = default_context.id
                                    debug(chat_id,
                                          'send_to matched, current_context_id is, inserting into heap: "%s"' % (current_context_id),
                                          bot)
                                    debug(chat_id,'posicion heap sendto %s'%(flow_position_.storage_value),bot)
                                    '''db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_id,
                                                               context_position = flow_position_.storage_value)'''
                                #send_to that context and clear the direction
                                debug(chat_id, 'saving current_context key with value: "%s"' % (action), bot)
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = int(action))
                                #----------------------------------------------------------------------------------
                                positionError=0
                                heap_ = db((db.bot_context_heap.storage_owner == chat_id)&                               (db.bot_context_heap.bot_id == bot.id)).select(db.bot_context_heap.ALL, orderby=~db.bot_context_heap.id).first()
                                if(heap_!= None):
                                    debug(chat_id,'contexto error%s action %s'%(heap_.context_id,action),bot)
                                    if int(heap_.context_id)==int(action):
                                        debug(chat_id,'posicion %s'%(heap_.context_position),bot)
                                        positionError=heap_.context_position
                                        #db(db.bot_context_heap.context_id == heap_.context_id).delete()
                                #-------------------------------------------------------------------
                                debug(chat_id, 'saving flow_position key with value: "%s"' % (positionError), bot)
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'flow_position',
                                                                        storage_value =positionError)
                                debug(chat_id, 'deleting send_to key 1', bot)
                                '''try:
                                    db(db.bot_context_heap.context_id == heap_.context_id).delete()
                                except:
                                    pass'''
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                debug(chat_id, 'recursive call %s' % (action), bot)
                                debug(chat_id, '-deleting should_value_ai key', bot)
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'should_value_ai')).delete()
                                return messenger(bot, conn)
                debug(chat_id, 'deleting send_to key 2', bot)
                db((db.bot_internal_storage.storage_owner == chat_id)&
                   (db.bot_internal_storage.bot_id == bot.id)&
                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
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
                if not current_context:
                    default_context = db((db.bot_context.bot_id == bot.id)&(db.bot_context.name == 'default')).select().first()
                    current_context = default_context.id
                else:
                    current_context = int(current_context.storage_value)
                context = db((db.bot_context.id == current_context)).select().first()
                #we now run the flow
                flow_position = db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                #debug(chat_id, 'flow position p1 "%s"' % (flow_position), bot)
                if flow_position:
                    #---------------------------------------------------------------
                    flow_position = int(flow_position.storage_value)
                    #debug(chat_id, 'flow position IF "%s"' % (flow_position), bot)
                else:
                    flow_position = 0
                should_value_ai = db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'should_value_ai')).select().first()
                import json
                try:
                    should_value_ai = json.loads(should_value_ai.storage_value)
                except:
                    should_value_ai = None
                try:
                    #-------------------------------------------------------------------------
                    #debug(chat_id, 'flow position TRY "%s"' % (flow_position), bot)
                    flow_item = context.context_json[context.name][flow_position]
                except:
                    flow_item = None
                debug(chat_id, 'flow position, context: "%s", "%s"' % (flow_position, context.name), bot)
                #r(dict(recipient = dict(id = chat_id),
                #                          message = dict(text = 'flow position: "%s"' %(flow_position))))
                debug(chat_id, 'Before Testing AI (%s)' % (json.dumps(should_value_ai)), bot)
                if should_value_ai:
                    flow_item_eval = should_value_ai
                    if flow_item_eval['type'] == 'checkPoint':
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = flow_position + 1)
                    if flow_item_eval['type'] == 'chatCenter':
                        if(chat_text=='Yes'):
                            db((db.conversation.bot_id==bot.id)&(db.conversation.storage_owner==chat_id)).update(need_chat_center=True)
                            r(dict(recipient = dict(id = chat_id),
                              message = dict(text = 'wait online...')))
                            return 0
                        #aca quedaria la respuesta para desactivar el bot
                    if flow_item_eval['type'] == 'validationText':
                        debug(chat_id, 'Starting ValidationText', bot)
                        validacion=0
                        if ('validation' in flow_item_eval):
                            validacion+=int(flow_item_eval['validation'])
                        if(validacion==1):#verificamos si la entrada es de tipo texto
                            validacion=1
                            try:
                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                            except:
                                pass
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        if(validacion==2):#verificamos si la entrada es de tipo numero
                            import re
                            if re.match("^\d+$",chat_text.lower()):
                                #fdebug.write('Es un numero \n')
                                validacion=2
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                            else:
                                validacion=0
                        if(validacion==3):#verificamos si la entrada es un email
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-_]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$',chat_text.lower()):
                                #fdebug.write('email correcto \n')
                                validacion=3
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                            else:
                                validacion=0
                        if(validacion==4):#verificamos si la entrada es de tipo fecha
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search("^((0[1-9])|((1|2)[0-9])|(30|31))/((0[1-9])|10|11|12)/((1|2)[0-9][0-9][0-9])$",chat_text.lower()):
                                #fdebug.write('fecha correcta \n')
                                validacion=4
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                            else:
                                validacion=0
                        if(validacion==5):#verificamos si la entrada es un NIT valido
                            debug(chat_id, 'Testing NIT validation', bot)
                            import re
                            if re.search('^(\d)+(-)(\d|k|K)$',chat_text.lower()):
                                try:
                                    #debug(chat_id, 'NIT', bot)
                                    val_nit = chat_text.replace("-", "")
                                    size_nit = len(val_nit)
                                    sum_nit = 0
                                    num_verificador = ""
                                    #debug(chat_id, 'for', bot)
                                    #debug(chat_id, 'size_nit ' + str(size_nit), bot)
                                    for num in val_nit:
                                        if size_nit > 1 :
                                            sum_nit += int(num) * size_nit
                                            size_nit = size_nit - 1
                                        else:
                                            num_verificador = num
                                    debug(chat_id, 'num_verificador ' + num_verificador, bot)
                                    debug(chat_id, 'sum_nit ' + str(sum_nit), bot)
                                    cociente = sum_nit//11
                                    total = sum_nit - (cociente*11)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    while cociente != 0 and total != 0:
                                        cociente = total//11
                                        total = total - (cociente*11)
                                    debug(chat_id, 'total' + str(total), bot)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    if num_verificador == "k" or num_verificador == "K":
                                        val = 11 - total
                                        if val == 10:
                                            #NIT valido
                                            validacion=5
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        else:
                                            validacion=0
                                    else:
                                        val = 11 - total
                                        debug(chat_id, 'val' + str(val), bot)
                                        if val == int(num_verificador):
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        elif val == 11 and int(num_verificador) == 0:
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        else:
                                            validacion=0
                                        debug(chat_id, 'validacion ' + str(validacion), bot)
                                except ValueError:
                                    validacion=0
                            else:
                                validacion=0
                        if(validacion==6):#verificamos si la entrada es un DPI valido
                            debug(chat_id, 'Testing DPI validation', bot)
                            import re
                            if re.search('^(\d){13}$',chat_text.lower()):
                                try:
                                    DPI = chat_text
                                    count_numero = 2
                                    total_numero = 0
                                    num_verificador = 0
                                    str_municipio = ""
                                    str_departamento = ""
                                    for num in DPI:
                                        if count_numero <= 9:
                                            total_numero += int(num) * count_numero
                                        elif count_numero == 10:
                                            num_verificador = int(num)
                                        elif count_numero == 11 or count_numero == 12:
                                            str_departamento = str_departamento + num
                                        elif count_numero == 13 or count_numero == 14:
                                            str_municipio = str_municipio + num
                                        count_numero = count_numero + 1
                                    debug(chat_id, 'total_numero ' + str(total_numero), bot)
                                    debug(chat_id, 'str_departamento ' + str(str_departamento), bot)
                                    debug(chat_id, 'str_municipio ' + str(str_municipio), bot)
                                    #banderas de validacion
                                    flag_departamento = False
                                    flag_municipio = False
                                    flag_codigo = False
                                    #validar que sea un departamento valido
                                    departamento = int(str_departamento)
                                    if departamento >= 1 and departamento <= 22:
                                        flag_departamento = True
                                    #validar que sea un municipio valido
                                    municipio = int(str_municipio)
                                    if munisPorDepto[departamento - 1] >= municipio:
                                        flag_municipio = True
                                    #validar que el codigo sea valido
                                    validar = total_numero%11
                                    if validar == num_verificador :
                                        flag_codigo = True
                                    if flag_departamento == True and flag_municipio == True and flag_codigo == True:
                                        validacion=6
                                        debug(chat_id, 'validacion 6 ', bot)
                                        #NIT valido
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                           (db.bot_internal_storage.bot_id == bot.id)&
                                           (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                        try:
                                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                                        except:
                                            pass
                                    else:
                                        validacion=0
                                        debug(chat_id, 'validacion 0 ', bot)
                                except ValueError:
                                    validacion=0
                                    debug(chat_id, 'validacion 0 error ', bot)
                            else:
                                validacion=0
                        if(validacion<1):
                            debug(chat_id, 'Validation is %s' % (validacion), bot)
                            selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                            retrys=0
                            try:
                                retrys=int(selretrys[0]['storage_value'].split("--")[0])
                            except:
                                retrys=0
                            debug(chat_id, 'Retries: %s' % (retrys), bot)
                            if(retrys>0):
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = flow_position)
                                flow_position=flow_position-1
                                flow_item = context.context_json[context.name][flow_position]
                                if retrys==1:
                                    flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                                       (db.bot_internal_storage.bot_id == bot.id)&
                                                       (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                    '''current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                                       (db.bot_internal_storage.bot_id == bot.id)&
                                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                    debug(chat_id,'VR validation context actual %s posicion actual %s' (current_context_.storage_value,flow_position_.storage_value),bot)
                                    db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_.storage_value,
                                                               context_position = int(flow_position_.storage_value)-1)'''
                                    #debug(chat_id,'If ultima validacion pos=%s'%(flow_position_.storage_value),bot)
                    if flow_item_eval['type'] == 'validationReply':
                        validacion=0
                        if ('validation' in flow_item_eval):
                            validacion+=int(flow_item_eval['validation'])
                        if(validacion==1):#verificamos si la entrada es de tipo texto
                            validacion=1
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                            try:
                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                            except:
                                pass
                        if(validacion==2):#verificamos si la entrada es de tipo numero
                            debug(chat_id,'validacion numero VR',bot)
                            import re
                            if re.match("^\d+$",chat_text.lower()):
                                debug(chat_id,' IF validacion numero VR',bot)
                                #fdebug.write('Es un numero \n')
                                validacion=2
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                            else:
                                debug(chat_id,' ELSE validacion numero VR',bot)
                                validacion=0
                        if(validacion==3):#verificamos si la entrada es un email
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-_]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$',chat_text.lower()):
                                #fdebug.write('email correcto \n')
                                validacion=3
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                            else:
                                validacion=0
                        if(validacion==4):#verificamos si la entrada es de tipo fecha
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search("^((0[1-9])|((1|2)[0-9])|(30|31))/((0[1-9])|10|11|12)/((1|2)[0-9][0-9][0-9])$",chat_text.lower()):
                                #fdebug.write('fecha correcta \n')
                                validacion=4
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                try:
                                    db(db.bot_context_heap.bot_id ==bot.id).delete()
                                except:
                                    pass
                            else:
                                validacion=0
                        if(validacion==5):#verificamos si la entrada es un NIT valido
                            debug(chat_id, 'Testing NIT validation', bot)
                            import re
                            if re.search('^(\d)+(-)(\d|k|K)$',chat_text.lower()):
                                try:
                                    #debug(chat_id, 'NIT', bot)
                                    val_nit = chat_text.replace("-", "")
                                    size_nit = len(val_nit)
                                    sum_nit = 0
                                    num_verificador = ""
                                    #debug(chat_id, 'for', bot)
                                    #debug(chat_id, 'size_nit ' + str(size_nit), bot)
                                    for num in val_nit:
                                        if size_nit > 1 :
                                            sum_nit += int(num) * size_nit
                                            size_nit = size_nit - 1
                                        else:
                                            num_verificador = num
                                    debug(chat_id, 'num_verificador ' + num_verificador, bot)
                                    debug(chat_id, 'sum_nit ' + str(sum_nit), bot)
                                    cociente = sum_nit//11
                                    total = sum_nit - (cociente*11)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    while cociente != 0 and total != 0:
                                        cociente = total//11
                                        total = total - (cociente*11)
                                    debug(chat_id, 'total' + str(total), bot)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    if num_verificador == "k" or num_verificador == "K":
                                        val = 11 - total
                                        if val == 10:
                                            #NIT valido
                                            validacion=5
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        else:
                                            validacion=0
                                    else:
                                        val = 11 - total
                                        debug(chat_id, 'val' + str(val), bot)
                                        if val == int(num_verificador):
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        elif val == 11 and int(num_verificador) == 0:
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            try:
                                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                                            except:
                                                pass
                                        else:
                                            validacion=0
                                        debug(chat_id, 'validacion ' + str(validacion), bot)
                                except ValueError:
                                    validacion=0
                            else:
                                validacion=0
                        if(validacion==6):#verificamos si la entrada es un DPI valido
                            debug(chat_id, 'Testing DPI validation', bot)
                            import re
                            if re.search('^(\d){13}$',chat_text.lower()):
                                try:
                                    DPI = chat_text
                                    count_numero = 2
                                    total_numero = 0
                                    num_verificador = 0
                                    str_municipio = ""
                                    str_departamento = ""
                                    for num in DPI:
                                        if count_numero <= 9:
                                            total_numero += int(num) * count_numero
                                        elif count_numero == 10:
                                            num_verificador = int(num)
                                        elif count_numero == 11 or count_numero == 12:
                                            str_departamento = str_departamento + num
                                        elif count_numero == 13 or count_numero == 14:
                                            str_municipio = str_municipio + num
                                        count_numero = count_numero + 1
                                    debug(chat_id, 'total_numero ' + str(total_numero), bot)
                                    debug(chat_id, 'str_departamento ' + str(str_departamento), bot)
                                    debug(chat_id, 'str_municipio ' + str(str_municipio), bot)
                                    #banderas de validacion
                                    flag_departamento = False
                                    flag_municipio = False
                                    flag_codigo = False
                                    #validar que sea un departamento valido
                                    departamento = int(str_departamento)
                                    if departamento >= 1 and departamento <= 22:
                                        flag_departamento = True
                                    #validar que sea un municipio valido
                                    municipio = int(str_municipio)
                                    if munisPorDepto[departamento - 1] >= municipio:
                                        flag_municipio = True
                                    #validar que el codigo sea valido
                                    validar = total_numero%11
                                    if validar == num_verificador :
                                        flag_codigo = True
                                    if flag_departamento == True and flag_municipio == True and flag_codigo == True:
                                        validacion=6
                                        debug(chat_id, 'validacion 6 ', bot)
                                        #NIT valido
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                           (db.bot_internal_storage.bot_id == bot.id)&
                                           (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                        try:
                                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                                        except:
                                            pass
                                    else:
                                        validacion=0
                                        debug(chat_id, 'validacion 0 ', bot)
                                except ValueError:
                                    validacion=0
                                    debug(chat_id, 'validacion 0 error ', bot)
                            else:
                                validacion=0
                        #fdebug.close()
                        if(validacion<1):
                            debug(chat_id,'no paso validaciones',bot)
                            selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                            retrys=0
                            try:
                                retrys=int(selretrys[0]['storage_value'].split("--")[0])
                            except:
                                retrys=0
                            if(retrys>0):
                                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = flow_position)
                                flow_position=flow_position-1
                                flow_item = context.context_json[context.name][flow_position]
                                if retrys==1:
                                    flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                                       (db.bot_internal_storage.bot_id == bot.id)&
                                                       (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                    variable=int(flow_position_.storage_value)-1
                                    debug(chat_id, 'Variable VR %s'%(variable), bot)
                                    '''db.bot_internal_error.update_or_insert((db.bot_internal_error.storage_owner == chat_id)&
                                                                     (db.bot_internal_error.bot_id == bot.id),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    position_flow =int(flow_position_.storage_value)-1)'''
                                #return messenger(bot, conn)
                            #else:
                                #r('sendMessage', dict(chat_id = chat_id,text = 'se han acabado los retrys enviando al contexto ... '))
                                #valsss=0
                                #return 0
                                #return messenger(bot, conn)
                    if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                        validacion=0
                        if ('validation' in flow_item_eval):
                            #fdebug.write(flow_item_eval['validation']+'\n')
                            validacion+=int(flow_item_eval['validation'])
                        debug(chat_id,
                              'does this element validates input?: "%s"' % (validacion),
                              bot)
                        if(validacion==1):#verificamos si la entrada es de tipo texto
                            #fdebug.write('Tipo texto: '+chat_text+'\n')
                            validacion=1
                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                        if(validacion==2):#verificamos si la entrada es de tipo numero
                            import re
                            if re.match("^\d+$",chat_text.lower()):
                                #fdebug.write('Es un numero \n')
                                validacion=2
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                            else:
                                validacion=0
                        if(validacion==3):#verificamos si la entrada es un email
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-_]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$',chat_text.lower()):
                                #fdebug.write('email correcto \n')
                                validacion=3
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                            else:
                                validacion=0
                        if(validacion==4):#verificamos si la entrada es de tipo fecha
                            #fdebug.write(chat_text+'\n')
                            import re
                            if re.search("^((0[1-9])|((1|2)[0-9])|(30|31))/((0[1-9])|10|11|12)/((1|2)[0-9][0-9][0-9])$",chat_text.lower()):
                                #fdebug.write('fecha correcta \n')
                                validacion=4
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                db(db.bot_context_heap.bot_id ==bot.id).delete()
                            else:
                                validacion=0
                        if(validacion==5):#verificamos si la entrada es un NIT valido
                            debug(chat_id, 'Testing NIT validation', bot)
                            import re
                            if re.search('^(\d)+(-)(\d|k|K)$',chat_text.lower()):
                                try:
                                    #debug(chat_id, 'NIT', bot)
                                    val_nit = chat_text.replace("-", "")
                                    size_nit = len(val_nit)
                                    sum_nit = 0
                                    num_verificador = ""
                                    #debug(chat_id, 'for', bot)
                                    #debug(chat_id, 'size_nit ' + str(size_nit), bot)
                                    for num in val_nit:
                                        if size_nit > 1 :
                                            sum_nit += int(num) * size_nit
                                            size_nit = size_nit - 1
                                        else:
                                            num_verificador = num
                                    debug(chat_id, 'num_verificador ' + num_verificador, bot)
                                    debug(chat_id, 'sum_nit ' + str(sum_nit), bot)
                                    cociente = sum_nit//11
                                    total = sum_nit - (cociente*11)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    while cociente != 0 and total != 0:
                                        cociente = total//11
                                        total = total - (cociente*11)
                                    debug(chat_id, 'total' + str(total), bot)
                                    #debug(chat_id, 'cociente ' + str(cociente), bot)
                                    if num_verificador == "k" or num_verificador == "K":
                                        val = 11 - total
                                        if val == 10:
                                            #NIT valido
                                            validacion=5
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                                        else:
                                            validacion=0
                                    else:
                                        val = 11 - total
                                        debug(chat_id, 'val' + str(val), bot)
                                        if val == int(num_verificador):
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                                        elif val == 11 and int(num_verificador) == 0:
                                            validacion=5
                                            #NIT valido
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                            db(db.bot_context_heap.bot_id ==bot.id).delete()
                                        else:
                                            validacion=0
                                        debug(chat_id, 'validacion ' + str(validacion), bot)
                                except ValueError:
                                    validacion=0
                            else:
                                validacion=0
                        if(validacion==6):#verificamos si la entrada es un DPI valido
                            debug(chat_id, 'Testing DPI validation', bot)
                            import re
                            if re.search('^(\d){13}$',chat_text.lower()):
                                try:
                                    DPI = chat_text
                                    count_numero = 2
                                    total_numero = 0
                                    num_verificador = 0
                                    str_municipio = ""
                                    str_departamento = ""
                                    for num in DPI:
                                        if count_numero <= 9:
                                            total_numero += int(num) * count_numero
                                        elif count_numero == 10:
                                            num_verificador = int(num)
                                        elif count_numero == 11 or count_numero == 12:
                                            str_departamento = str_departamento + num
                                        elif count_numero == 13 or count_numero == 14:
                                            str_municipio = str_municipio + num
                                        count_numero = count_numero + 1
                                    debug(chat_id, 'total_numero ' + str(total_numero), bot)
                                    debug(chat_id, 'str_departamento ' + str(str_departamento), bot)
                                    debug(chat_id, 'str_municipio ' + str(str_municipio), bot)
                                    #banderas de validacion
                                    flag_departamento = False
                                    flag_municipio = False
                                    flag_codigo = False
                                    #validar que sea un departamento valido
                                    departamento = int(str_departamento)
                                    if departamento >= 1 and departamento <= 22:
                                        flag_departamento = True
                                    #validar que sea un municipio valido
                                    municipio = int(str_municipio)
                                    if munisPorDepto[departamento - 1] >= municipio:
                                        flag_municipio = True
                                    #validar que el codigo sea valido
                                    validar = total_numero%11
                                    if validar == num_verificador :
                                        flag_codigo = True
                                    if flag_departamento == True and flag_municipio == True and flag_codigo == True:
                                        validacion=6
                                        debug(chat_id, 'validacion 6 ', bot)
                                        #NIT valido
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'retryText')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                           (db.bot_internal_storage.bot_id == bot.id)&
                                           (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                            (db.bot_internal_storage.bot_id == bot.id)&
                                            (db.bot_internal_storage.storage_key == 'send_to')).delete()
                                        db(db.bot_context_heap.bot_id ==bot.id).delete()
                                    else:
                                        validacion=0
                                        debug(chat_id, 'validacion 0 ', bot)
                                except ValueError:
                                    validacion=0
                                    debug(chat_id, 'validacion 0 error ', bot)
                            else:
                                validacion=0
                        #fdebug.close()
                        if flow_item_eval['type'] == 'smartReply':
                            debug(chat_id, 'flow_item_eval: "%s"' % (flow_item_eval), bot)
                            debug(chat_id, 'validacion: "%i"' % (validacion), bot)
                            #check for smartReply with option without send_to
                            for reply in flow_item_eval['quick_replies']:
                                valuation = chat_text.strip() == reply['title'].strip()
                                debug(chat_id, 'valuation: "%i"' % (valuation), bot)
                                debug(chat_id,
                                      'testing string1 before trying AI: "%s", string2: "%s"' % (chat_text.strip(),
                                                                                               reply['title'].strip()),
                                      bot)
                                if valuation:
                                    validacion = 1
                                    debug(chat_id,
                                      'option matched: "%s", string2: "%s"' % (chat_text.strip(),reply['title'].strip()),
                                      bot)
                                    continue
                        debug(chat_id, 'evaluating smart_text/smart_reply, omitir_IA: "%s"' % (validacion), bot)
                        if(validacion<1):
                            debug(chat_id, '1. Validation is %s' % (validacion), bot)
                            selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                            retrys=0
                            try:
                                retrys=int(selretrys[0]['storage_value'].split("--")[0])
                            except:
                                retrys=0
                            debug(chat_id, 'Retries: %s' % (retrys), bot)
                        if(validacion<1):
                            #Smart response validation request
                            import requests
                            params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                            response = requests.get('http://localhost:5000/parse', params=params)
                            #context = response['intent']
                            #import json
                            json_string = response.json()
                            debug(chat_id, '2. evaluating AI: "%s"' % (response.text), bot)
                            #getting the conext name
                            context_= None
                            import traceback
                            try:
                                context_ = json_string['intent']['name']
                                import datetime
                                current_date = datetime.datetime.now()
                                current_time = datetime.datetime.now().time()
                                db.ai_request.insert(bot_id = bot.id,
                                                     storage_owner = chat_id,
                                                     request_time = current_time,
                                                     request_date = current_date,
                                                     medium = 'messenger',
                                                     status = 'success',
                                                     ccontent = chat_text,
                                                     ai_response = context_)
                            except:
                                import datetime
                                current_date = datetime.datetime.now()
                                current_time = datetime.datetime.now().time()
                                debug(chat_id, 'error calling AI: "%s"' % (traceback.format_exc()), bot)
                                db.ai_request.insert(bot_id = bot.id,
                                                     storage_owner = chat_id,
                                                     request_time = current_time,
                                                     request_date = current_date,
                                                     medium = 'messenger',
                                                     status = 'error',
                                                     ccontent = chat_text,
                                                     ai_response = '')
                            if context_:
                                debug(chat_id, 'context_ %s' % (context_), bot)
                                context_id = db((db.bot_context.bot_id == bot.id)
                                            &(db.bot_intent.name == context_)
                                            &(db.bot_intent.context_id==db.bot_context.id)).select(db.bot_context.id).first()
                                debug(chat_id, 'AI sending to context: "%s", "%s"' % (context_, context_id), bot)
                                if context_id:
                                    flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                    debug(chat_id, 'flow_position %s' % (flow_position_.storage_value), bot)
                                    if(int(flow_position_.storage_value)!=0):
                                        current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                           (db.bot_internal_storage.bot_id == bot.id)&
                                           (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                        debug(chat_id, 'current_context_ %s' % (current_context_), bot)
                                        current_context_id = 0
                                        if(current_context_!=None):
                                            current_context_id = current_context_.storage_value
                                            debug(chat_id, 'current context_id %s' % (current_context_id), bot)
                                        else:
                                            default_context = db((db.bot_context.bot_id == bot.id)
                                                                 &(db.bot_context.name == 'default')).select().first()
                                            current_context_id = default_context.id
                                            debug(chat_id, 'default context_id %s' % (current_context_id), bot)
                                        db.bot_context_heap.insert(storage_owner = chat_id,
                                                                   bot_id = bot.id,
                                                                   context_id = current_context_id,
                                                                   context_position = flow_position_.storage_value)
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
                                    debug(chat_id, '-deleting should_value_ai key', bot)
                                    db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'should_value_ai')).delete()
                                    return messenger(bot, conn)
#
                debug(chat_id, 'After Testing AI, Before testing validation and smart items', bot)
                if flow_item['type'] in ('checkPoint',
                                         'chatCenter',
                                         'validationText',
                                         'validationReply',
                                         'smartText',
                                         'smartReply'):
                    debug(chat_id, '+adding should_value_ai key for next run', bot)
                    import json
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'should_value_ai'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'should_value_ai',
                                                            storage_value = json.dumps(flow_item))
                else:
                    debug(chat_id, '-deleting should_value_ai key', bot)
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                       (db.bot_internal_storage.bot_id == bot.id)&
                       (db.bot_internal_storage.storage_key == 'should_value_ai')).delete()
                debug(chat_id, 'After Validation and Smart Items', bot)
                #END SMART OBJECTS
                #save the answer of the cliente in the bot_storage table
                #checking if the flow item has the "store" property
                if flow_item!= None:
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
                #debug(chat_id,'nextPOs %s contextjson %s'%(next_position,len(context.context_json[context.name])),bot)
                if next_position >= len(context.context_json[context.name]):
                    debug(chat_id,'entro al if heap',bot)
                    heap_ = db((db.bot_context_heap.storage_owner == chat_id)&
                               (db.bot_context_heap.bot_id == bot.id)).select(db.bot_context_heap.ALL, orderby=~db.bot_context_heap.id).first()
                    if(heap_!= None):
                        debug(chat_id,'entro al if heap is not none',bot)
                        next_position=heap_.context_position
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                                     (db.bot_internal_storage.storage_key == 'current_context'),
                                                                    storage_owner = chat_id,
                                                                    bot_id = bot.id,
                                                                    storage_key = 'current_context',
                                                                    storage_value = heap_.context_id)
                        debug(chat_id,'IF heap context %s posicion %s (delete context_heap)'%(heap_.context_id,next_position),bot)
                        #--------------------------------------------------------------------------
                        #db(db.bot_context_heap.id == heap_.id).delete()
                    else:
                        next_position = 0
                        debug(chat_id,'entro al else heap',bot)
                        #find the parent context and set to it
                        if context.parent_context is not None:
                            debug(chat_id,'entro al if del else heap',bot)
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = context.parent_context.id)
                            #debug(chat_id,'ELSE heap context %s'%(context.parent_context.id),bot)
                db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'flow_position',
                                                            storage_value = next_position)
                #debug(chat_id,'ELSE heap posicion %s'%(next_position),bot)
                #phantom
                flow_position_phantom_count = db((db.bot_phantom_context.storage_owner == chat_id)&
                                   (db.bot_phantom_context.bot_id == bot.id)).count()
                if(flow_position_phantom_count>0):
                    flow_position_phantom = db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).select().first()
                    flow_position=int(str(flow_position_phantom.flow_position))
                    if(flow_position==len(flow_position_phantom.context_json[flow_position_phantom.name])):
                        db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).delete()
                        return messenger(bot, conn)
                    else:
                        flow_item_phantom = flow_position_phantom.context_json[flow_position_phantom.name][int(str(flow_position_phantom.flow_position))]
                        context.context_json=flow_position_phantom.context_json
                        context.name=flow_position_phantom.name
                        flow_item=flow_item_phantom
                        try:
                            should_store_key = flow_item['store']
                            db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                       (db.bot_storage.storage_owner == chat_id)&
                                                       (db.bot_storage.storage_key == should_store_key),
                                                       storage_owner = chat_id,
                                                       bot_id = bot.id,
                                                       storage_key = should_store_key,
                                                       storage_value = chat_text)
                        except:
                            val=1
                        db((db.bot_phantom_context.storage_owner == chat_id)&
                           (db.bot_phantom_context.bot_id == bot.id)).update(flow_position=(int(str(flow_position_phantom.flow_position))+1))
                #THIS CALL CAN CHANGE THE CONTEXT AND POSITION COMPLETELY
                debug(chat_id, 'ended pre-evaluations, calling item: "%s"' % (flow_item['type']), bot)
                #r(dict(recipient = dict(id = chat_id),
                #                          message = dict(text = 'calling next item %s' %(
                #                                         flow_item['type']))))
                flow[flow_item['type']](chat_id, flow_item,
                                        bot = bot,
                                        flow_position = flow_position,
                                        current_context = current_context,
                                        context = context)

                #value
                if flow_item['type'] == 'sender_action':
                    return messenger(bot, conn)
                if flow_item['type'] == 'end':
                    return messenger(bot, conn)
                if flow_item['type'] == 'attachment':
                    return messenger(bot, conn)
                if flow_item['type'] == 'decisionRest':
                    return messenger(bot, conn)
                if flow_item['type'] == 'countValidation':
                    return messenger(bot, conn)
                #captcha_verification
                '''if flow_item['type'] == 'captcha':
                    return r(dict(recipient = dict(id = chat_id),
                            message = "captcha here!"))'''
                    #return messenger(bot, conn)

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
            def validationText(chat_id, flow_item, bot, **vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                retrys=0
                #r('sendMessage', dict(chat_id = chat_id,text = 'def'))
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                #r('sendMessage', dict(chat_id = chat_id,text = 'numero de retrys '+str(retrys)))
                if(retrys<1):
                  try:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(str(flow_item['sendTo'])))

                  except:
                    print("Error")
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
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                    return telegram(bot, conn)
                else:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryText'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'retryText',
                                                            storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
                    return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content']))
            def validationReply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                retrys=0
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                if(retrys<1):
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(str(flow_item['sendTo'])))
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
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                    return telegram(bot, conn)
                else:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'retryReply',
                                                            storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
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
            def chatCenter(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                keyboard=[]
                keyboard.append('Yes')
                keyboard.append('No')
                return r('sendMessage', dict(chat_id = chat_id,
                                             text = flow_item['content'],
                                             reply_markup = dict(keyboard = [keyboard], one_time_keyboard = True)))
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
            def checkPoint(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                import datetime
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.bot_checkpoint.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       checkpoint_date = current_date,
                                       checkpoint_time = current_time,
                                       checkpoint_name = flow_item['content'],
                                       medium = 'telegram')
                return telegram(bot, conn)
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
            def quick_reply(chat_id,flow_item, bot, **vars):
                debug(chat_id,'referencia: %s'%(reference),bot)
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
                    if value:
                        data[key['in']] = value.storage_value
                    else:
                        data[key['in']] = None
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)[:4096]
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)[:4096]
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = result))
            def decisionRest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    if value:
                        data[key['in']] = value.storage_value
                    else:
                        data[key['in']] = None
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                qr = []
                for q in flow_item['quick_replies']:
                    snd = q['sendTo']
                    val = q['value']
                    if(result==val):
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'current_context'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'current_context',
                                                                        storage_value = int(snd))
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                            storage_owner = chat_id,
                                                                            bot_id = bot.id,
                                                                            storage_key = 'flow_position',
                                                                            storage_value = 0)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return 0
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest':rest,
                    'attachment': attachment,
                    'smartText': smartText,
                    'chatCenter':chatCenter,
                    'validationText':validationText,
                    'validationReply':validationReply,
                    'checkPoint':checkPoint,
                    'decisionRest':decisionRest,
                    'smartReply':smartReply}
            #raise Exception(vars)
            chat_id = vars['id']
            chat_user_name = vars['first_name']
            chat_text = vars['text']
            resp=db((db.conversation.bot_id==bot.id)&(db.conversation.storage_owner==chat_id))
            needchat=False
            try:
                needchat=resp.select(db.conversation.need_chat_center)[0]['need_chat_center']
            except:
                needchat=False
            if(needchat):
                def log_conversationtrue(chat_id, chat_text, bot, type,content_type):
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
                                       content_type = content_type,
                                       need_chat_center=True)
                log_conversationtrue(chat_id, chat_text, bot, 'received','text')
                return 0
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
                        import unicodedata
                        if chat_text.strip() == match.strip():
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
            flow_item = None
            try:
                flow_item = context.context_json[context.name][flow_position]
            except:
                flow_item = None
            next_position = flow_position + 1
            #Make it back to 0
            if next_position >= len(context.context_json[context.name]):
                next_position = 0
                #find the parent context and set to it
                if context.parent_context is not None:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'current_context'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'current_context',
                                                            storage_value = context.parent_context.id)
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
                if flow_item_eval['type'] == 'checkPoint':
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = next_position)
                if flow_item_eval['type'] == 'chatCenter':
                        if(chat_text=='Yes'):
                            db((db.conversation.bot_id==bot.id)&(db.conversation.storage_owner==chat_id)).update(need_chat_center=True)
                            return r('sendMessage', dict(chat_id = chat_id,
                                             text = 'wait online...'))
                if flow_item_eval['type'] == 'validationText':
                    validacion=0
                    if ('validation' in flow_item_eval):
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        validacion=1
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                        retrys=0
                        try:
                            retrys=int(selretrys[0]['storage_value'].split("--")[0])
                        except:
                            retrys=0
                        if(retrys>0):
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = flow_position)
                            #return telegram(bot, conn)
                            flow_position=flow_position-1
                            flow_item = context.context_json[context.name][flow_position]
                        else:
                            #r('sendMessage', dict(chat_id = chat_id,text = '.'))
                            valss=9
                            return 0
                            #return telegram(bot, conn)
                if flow_item_eval['type'] == 'validationReply':
                    validacion=0
                    if ('validation' in flow_item_eval):
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        validacion=1
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                        retrys=0
                        try:
                            retrys=int(selretrys[0]['storage_value'].split("--")[0])
                        except:
                            retrys=0
                        if(retrys>0):
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = flow_position)
                            flow_position=flow_position-1
                            flow_item = context.context_json[context.name][flow_position]
                            #return telegram(bot, conn)
                        else:
                            #r('sendMessage', dict(chat_id = chat_id,text = 'se han acabado los retrys enviando al contexto ... '))
                            valss=9
                            return 0
                            #return telegram(bot, conn)
                if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                    validacion=0
                    if ('validation' in flow_item_eval):
                        #fdebug.write(flow_item_eval['validation']+'\n')
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        #fdebug.write('Tipo texto: '+chat_text+'\n')
                        validacion=1
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        fdebug.write(chat_text+'\n')
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        #Smart response validation request
                        import requests
                        params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                        response = requests.get('http://localhost:5000/parse', params=params)
                        #context = response['intent']
                        #import json
                        json_string = response.json()
                        context_= None
                        try:
                            context_ = json_string['intent']['name']
                            import datetime
                            current_date = datetime.datetime.now()
                            current_time = datetime.datetime.now().time()
                            db.ai_request.insert(bot_id = bot.id,
                                                   storage_owner = chat_id,
                                                   request_time = current_time,
                                                   request_date = current_date,
                                                   medium = 'telegram',
                                                   status = 'success',
                                                   ccontent = chat_text,
                                                   ai_response = context_)
                        except:
                            import datetime
                            current_date = datetime.datetime.now()
                            current_time = datetime.datetime.now().time()
                            db.ai_request.insert(bot_id = bot.id,
                                                   storage_owner = chat_id,
                                                   request_time = current_time,
                                                   request_date = current_date,
                                                   medium = 'telegram',
                                                   status = 'error',
                                                   ccontent = chat_text,
                                                   ai_response = '')
                            return telegram(bot, conn)
                        #getting the conext name
                        myfile = os.path.join('/home/rasa/rasa_nlu/sample_configs/', 'Project_'+ str(bot.id)+'.log')
                        f = open(myfile,'w')
                        f.write(context_)
                        f.write(str(json_string))
                        f.write('\n'+' id:')
                        f.write(str(bot.id)+'\n')
                        if context_:
                            context_id = db((db.bot_context.bot_id == bot.id)
                                            &(db.bot_intent.name == context_)
                                            &(db.bot_intent.context_id==db.bot_context.id)).select(db.bot_context.id).first()
                            if context_id:
                                f.write(str(context_id)+'\n')
                                #send_to that context and clear the direction
                                flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                if(int(flow_position_.storage_value)!=0):
                                    current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                    current_context_id = 0
                                    if(current_context_!=None):
                                        current_context_id = current_context_.storage_value
                                    else:
                                        default_context = db((db.bot_context.bot_id == bot.id)
                                                             &(db.bot_context.name == 'default')).select().first()
                                        current_context_id = default_context.id

                                    db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_id,
                                                               context_position = flow_position_.storage_value)
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
                                return telegram(bot, conn)
                        f.close()
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
            #phantom
            flow_position_phantom_count = db((db.bot_phantom_context.storage_owner == chat_id)&
                                   (db.bot_phantom_context.bot_id == bot.id)).count()
            if(flow_position_phantom_count>0):
                flow_position_phantom = db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).select().first()
                flow_position=int(str(flow_position_phantom.flow_position))
                if(flow_position==len(flow_position_phantom.context_json[flow_position_phantom.name])):
                    db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).delete()
                    return telegram(bot, conn)
                else:
                    flow_item_phantom = flow_position_phantom.context_json[flow_position_phantom.name][int(str(flow_position_phantom.flow_position))]
                    context.context_json=flow_position_phantom.context_json
                    context.name=flow_position_phantom.name
                    flow_item=flow_item_phantom
                    try:
                        should_store_key = flow_item['store']
                        db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                       (db.bot_storage.storage_owner == chat_id)&
                                                       (db.bot_storage.storage_key == should_store_key),
                                                       storage_owner = chat_id,
                                                       bot_id = bot.id,
                                                       storage_key = should_store_key,
                                                       storage_value = chat_text)
                    except:
                        val=1
                    db((db.bot_phantom_context.storage_owner == chat_id)&
                           (db.bot_phantom_context.bot_id == bot.id)).update(flow_position=(int(str(flow_position_phantom.flow_position))+1))
                        #r(dict(recipient = dict(id = chat_id),message = dict(text = str(len(flow_position_phantom.context_json[flow_position_phantom.name])))))
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
            if flow_item['type'] == 'attachment':
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
            def validationText(chat_id, flow_item, bot, **vars):
                keyboard = []
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                retrys=0
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                if(retrys<1):
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(str(flow_item['sendTo'])))
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
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                    return website(bot, conn)
                else:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryText'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'retryText',
                                                            storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
                    return r('sendMessage', dict(chat_id = chat_id,text = flow_item['content']))
            def validationReply(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                retrys=0
                try:
                    selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                    retrys=int(selretrys[0]['storage_value'].split("--")[0])-1
                except:
                    retrys=int(flow_item['retry'])
                    if(int(flow_item['retry'])==0):
                        retrys=10000
                if(retrys<1):
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = int(str(flow_item['sendTo'])))
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
                    db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                    return website(bot, conn)
                else:
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                             (db.bot_internal_storage.storage_key == 'retryReply'),
                                                            storage_owner = chat_id,
                                                            bot_id = bot.id,
                                                            storage_key = 'retryReply',
                                                            storage_value =str( str(retrys)+"--"+str(flow_item['sendTo'])))
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
            def end(chat_id, flow_item, bot, flow_position, current_context, context, **vars):
                log_conversation(chat_id, '<%s>'%(flow_item['action']), bot.id, 'sent','text')
                if flow_item['action'] == 'return':
                    #find the parent context and set to it
                    next_position_ = 0
                    heap_ = db((db.bot_context_heap.storage_owner == chat_id)&
                               (db.bot_context_heap.bot_id == bot.id)).select(db.bot_context_heap.ALL, orderby=~db.bot_context_heap.id).first()
                    if(heap_ is not None):
                        next_position_ = 0
                    else:
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
                                                                        storage_value = next_position_)
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
            def checkPoint(chat_id, flow_item, bot, **vars):
                log_conversation(chat_id, flow_item['content'], bot.id, 'sent','text')
                import datetime
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.bot_checkpoint.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       checkpoint_date = current_date,
                                       checkpoint_time = current_time,
                                       checkpoint_name = flow_item['content'],
                                       medium = 'website')
                return website(bot, conn)
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
                    if value:
                        data[key['in']] = value.storage_value
                    else :
                        data[key['in']] = None
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    try:
                        res = requests.get(flow_item['url'], params = data)
                        result = xmlescape(res.text)
                    except:
                        result = 'No se pudo conectar al sistema de cambio de contraseña, intente más tarde'
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return r('sendMessage', dict(chat_id = chat_id,text = result))
            def decisionRest(chat_id, flow_item, bot, **vars):
                import requests
                result = ''
                ##This is the array holding variable names I want
                data = dict()
                for key in flow_item['keys'] if flow_item['keys'] else []:
                    value = db.bot_storage((db.bot_storage.bot_id == bot)&
                                           (db.bot_storage.storage_owner == chat_id)&
                                           (db.bot_storage.storage_key == key['out'])) #This is the name of the variable in the database
                    if value:
                        data[key['in']] = value.storage_value
                    else:
                        data[key['in']] = None
                if flow_item['method'] == 'POST':
                    res = requests.post(flow_item['url'], data = data)
                    result = xmlescape(res.text)
                elif flow_item['method'] == 'GET':
                    res = requests.get(flow_item['url'], params = data)
                    result = xmlescape(res.text)
                qr = []
                for q in flow_item['quick_replies']:
                    snd = q['sendTo']
                    val = q['value']
                    if(result==val):
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                                         (db.bot_internal_storage.storage_key == 'current_context'),
                                                                        storage_owner = chat_id,
                                                                        bot_id = bot.id,
                                                                        storage_key = 'current_context',
                                                                        storage_value = int(snd))
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                             (db.bot_internal_storage.bot_id == bot.id)&
                                                                             (db.bot_internal_storage.storage_key == 'flow_position'),
                                                                            storage_owner = chat_id,
                                                                            bot_id = bot.id,
                                                                            storage_key = 'flow_position',
                                                                            storage_value = 0)
                log_conversation(chat_id, "<%s>"%(result), bot.id, 'sent','text')
                return 0
            flow = {'text': text,
                    'quick_reply': quick_reply,
                    'sender_action': sender_action,
                    'end':end,
                    'rest': rest,
                    'smartText':smartText,
                    'validationText':validationText,
                    'validationReply':validationReply,
                    'checkPoint':checkPoint,
                    'decisionRest':decisionRest,
                    'smartReply':smartReply}
            #raise Exception(vars)
            chat_id = vars['id']
            chat_user_name = vars['first_name']
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
                        import unicodedata
                        if chat_text.strip() == match.strip():
                            #send_to that context and clear the direction

                            flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                            if(int(flow_position_.storage_value)!=0):
                                current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                current_context_id = 0
                                if(current_context_!=None):
                                    current_context_id = current_context_.storage_value
                                else:
                                    default_context = db((db.bot_context.bot_id == bot.id)
                                                         &(db.bot_context.name == 'default')).select().first()
                                    current_context_id = default_context.id

                                db.bot_context_heap.insert(storage_owner = chat_id,
                                                           bot_id = bot.id,
                                                           context_id = current_context_id,
                                                           context_position = flow_position_.storage_value)

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

            if not current_context:
                default_context = db((db.bot_context.bot_id == bot.id)&(db.bot_context.name == 'default')).select().first()
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
            flow_item = None
            try:
                flow_item = context.context_json[context.name][flow_position]
            except:
                flow_item = None
            next_position = flow_position + 1
            #Make it back to 0
            if next_position >= len(context.context_json[context.name]):
                heap_ = db((db.bot_context_heap.storage_owner == chat_id)&
                               (db.bot_context_heap.bot_id == bot.id)).select(db.bot_context_heap.ALL, orderby=~db.bot_context_heap.id).first()
                if(heap_!= None):
                    next_position=heap_.context_position
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = heap_.context_id)
                    db(db.bot_context_heap.id == heap_.id).delete()
                else:
                    next_position = 0
                    #find the parent context and set to it
                    if context.parent_context is not None:
                        db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'current_context'),
                                                                storage_owner = chat_id,
                                                                bot_id = bot.id,
                                                                storage_key = 'current_context',
                                                                storage_value = context.parent_context.id)
            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                     (db.bot_internal_storage.bot_id == bot.id)&
                                                     (db.bot_internal_storage.storage_key == 'flow_position'),
                                                    storage_owner = chat_id,
                                                    bot_id = bot.id,
                                                    storage_key = 'flow_position',
                                                    storage_value = next_position)
            log_conversation(chat_id, chat_text, bot.id, 'received','text')
            myfile = os.path.join('/home/rasa/rasa_nlu/sample_configs/', 'Project_'+ str(bot.id)+'.log')
            f = open(myfile,'w')
            f.write(str(flow_position))
            f.close()
            if flow_position > 0:
                flow_item_eval = context.context_json[context.name][flow_position - 1]
                #SMART OBJECTS
                if flow_item_eval['type'] == 'checkPoint':
                    db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = next_position)
                if flow_item_eval['type'] == 'validationReply':
                    validacion=0
                    if ('validation' in flow_item_eval):
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        validacion=1
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryReply')).delete()
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'retryReply')).select(db.bot_internal_storage.storage_value)
                        retrys=0
                        try:
                            retrys=int(selretrys[0]['storage_value'].split("--")[0])
                        except:
                            retrys=0
                        if(retrys>0):
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = flow_position)
                            flow_position=flow_position-1
                            flow_item = context.context_json[context.name][flow_position]
                            #return website(bot, conn)
                        else:
                            #r('sendMessage', dict(chat_id = chat_id,text = 'se han acabado los retrys enviando al contexto ... '))
                            #return website(bot, conn)
                            return 0
                if flow_item_eval['type'] == 'validationText':
                    validacion=0
                    if ('validation' in flow_item_eval):
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        validacion=1
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                        db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                               (db.bot_internal_storage.bot_id == bot.id)&
                               (db.bot_internal_storage.storage_key == 'retryText')).delete()
                            db((db.bot_internal_storage.storage_owner == chat_id)&
                                   (db.bot_internal_storage.bot_id == bot.id)&
                                   (db.bot_internal_storage.storage_key == 'send_to')).delete()
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        selretrys=db((db.bot_internal_storage.storage_owner == chat_id)&
                                                                 (db.bot_internal_storage.bot_id == bot.id)&
                                                                 (db.bot_internal_storage.storage_key == 'retryText')).select(db.bot_internal_storage.storage_value)
                        retrys=0
                        try:
                            retrys=int(selretrys[0]['storage_value'].split("--")[0])
                        except:
                            retrys=0
                        if(retrys>0):
                            db.bot_internal_storage.update_or_insert((db.bot_internal_storage.storage_owner == chat_id)&
                                                         (db.bot_internal_storage.bot_id == bot.id)&
                                                         (db.bot_internal_storage.storage_key == 'flow_position'),
                                                        storage_owner = chat_id,
                                                        bot_id = bot.id,
                                                        storage_key = 'flow_position',
                                                        storage_value = flow_position)
                            flow_position=flow_position-1
                            flow_item = context.context_json[context.name][flow_position]
                            #return website(bot, conn)
                        else:
                            #r('sendMessage', dict(chat_id = chat_id,text = 'se han acabado los retrys enviando al contexto ... '))
                            vasss=99
                            return 0
                            #return website(bot, conn)
                if flow_item_eval['type'] == 'smartText' or flow_item_eval['type'] == 'smartReply':
                    #paradebug=os.path.join('/home/rasa/rasa_nlu/sample_configs/','debugricky.txt')
                    #fdebug=open(paradebug,'w')
                    validacion=0
                    if ('validation' in flow_item_eval):
                        #fdebug.write(flow_item_eval['validation']+'\n')
                        validacion+=int(flow_item_eval['validation'])
                    if(validacion==1):#verificamos si la entrada es de tipo texto
                        #fdebug.write('Tipo texto: '+chat_text+'\n')
                        validacion=1
                    if(validacion==2):#verificamos si la entrada es de tipo numero
                        fdebug.write(chat_text+'\n')
                        import re
                        if re.match("^\d+$",chat_text.lower()):
                            #fdebug.write('Es un numero \n')
                            validacion=2
                        else:
                            validacion=0
                    if(validacion==3):#verificamos si la entrada es un email
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search('[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}',chat_text.lower()):
                            #fdebug.write('email correcto \n')
                            validacion=3
                        else:
                            validacion=0
                    if(validacion==4):#verificamos si la entrada es de tipo fecha
                        #fdebug.write(chat_text+'\n')
                        import re
                        if re.search("(\d |\d\d)(.|-|/)(\d |\d\d)(.|-|/)(d\d\d\d|\d\d)",chat_text.lower()):
                            #fdebug.write('fecha correcta \n')
                            validacion=4
                        else:
                            validacion=0
                    #fdebug.close()
                    if(validacion<1):
                        #Smart response validation request
                        import requests
                        params = (('q', chat_text),('project', 'Project_'+ str(bot.id)))
                        response = requests.get('http://localhost:5000/parse', params=params)
                        #context = response['intent']
                        #import json
                        json_string = response.json()
                        context_ = None
                        try:
                            context_ = json_string['intent']['name']
                            import datetime
                            current_date = datetime.datetime.now()
                            current_time = datetime.datetime.now().time()
                            db.conversation.insert(bot_id = bot.id,
                                                   storage_owner = chat_id,
                                                   request_time = current_time,
                                                   request_date = current_date,
                                                   medium = 'web_site',
                                                   status = 'success',
                                                   ccontent = chat_text,
                                                   ai_response = context_)
                        except:
                            import datetime
                            current_date = datetime.datetime.now()
                            current_time = datetime.datetime.now().time()
                            db.conversation.insert(bot_id = bot.id,
                                                   storage_owner = chat_id,
                                                   request_time = current_time,
                                                   request_date = current_date,
                                                   medium = 'web_site',
                                                   status = 'error',
                                                   ccontent = chat_text,
                                                   ai_response = '')
                            return website(bot, conn)
                        #getting the conext name
                        myfile = os.path.join('/home/rasa/rasa_nlu/sample_configs/', 'Project_'+ str(bot.id)+'.log')
                        f = open(myfile,'w')
                        f.write(context_)
                        f.write('\n'+' id:')
                        f.write(str(bot.id)+'\n')
                        if context_:
                            context_id = db((db.bot_context.bot_id == bot.id)
                                            &(db.bot_intent.name == context_)
                                            &(db.bot_intent.context_id==db.bot_context.id)).select(db.bot_context.id).first()
                            if context_id:
                                f.write(str(context_id)+'\n')
                                flow_position_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                               (db.bot_internal_storage.bot_id == bot.id)&
                                               (db.bot_internal_storage.storage_key == 'flow_position')).select().first()
                                if(int(flow_position_.storage_value)!=0):
                                    current_context_ = db((db.bot_internal_storage.storage_owner == chat_id)&
                                       (db.bot_internal_storage.bot_id == bot.id)&
                                       (db.bot_internal_storage.storage_key == 'current_context')).select().first()
                                    current_context_id = 0
                                    if(current_context_!=None):
                                        current_context_id = current_context_.storage_value
                                    else:
                                        default_context = db((db.bot_context.bot_id == bot.id)
                                                             &(db.bot_context.name == 'default')).select().first()
                                        current_context_id = default_context.id

                                    db.bot_context_heap.insert(storage_owner = chat_id,
                                                               bot_id = bot.id,
                                                               context_id = current_context_id,
                                                               context_position = flow_position_.storage_value)
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
                        f.close()
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
            #phantom
            flow_position_phantom_count = db((db.bot_phantom_context.storage_owner == chat_id)&
                                   (db.bot_phantom_context.bot_id == bot.id)).count()
            if(flow_position_phantom_count>0):
                flow_position_phantom = db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).select().first()
                flow_position=int(str(flow_position_phantom.flow_position))
                if(flow_position==len(flow_position_phantom.context_json[flow_position_phantom.name])):
                    db((db.bot_phantom_context.storage_owner == chat_id)&
                                       (db.bot_phantom_context.bot_id == bot.id)).delete()
                    return website(bot, conn)
                else:
                    flow_item_phantom = flow_position_phantom.context_json[flow_position_phantom.name][int(str(flow_position_phantom.flow_position))]
                    context.context_json=flow_position_phantom.context_json
                    context.name=flow_position_phantom.name
                    flow_item=flow_item_phantom
                    try:
                        should_store_key = flow_item['store']
                        db.bot_storage.update_or_insert((db.bot_storage.bot_id == bot.id)&
                                                       (db.bot_storage.storage_owner == chat_id)&
                                                       (db.bot_storage.storage_key == should_store_key),
                                                       storage_owner = chat_id,
                                                       bot_id = bot.id,
                                                       storage_key = should_store_key,
                                                       storage_value = chat_text)
                    except:
                        val=1
                    db((db.bot_phantom_context.storage_owner == chat_id)&
                           (db.bot_phantom_context.bot_id == bot.id)).update(flow_position=(int(str(flow_position_phantom.flow_position))+1))
                        #r(dict(recipient = dict(id = chat_id),message = dict(text = str(len(flow_position_phantom.context_json[flow_position_phantom.name])))))
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
            if flow_item['type'] == 'attachment':
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