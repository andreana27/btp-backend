# -*- coding: utf-8 -*-

auth.settings.allow_basic_login = True
#@auth.requires(token_auth, requires_login=False)
@cors_allow
@request.restful()
def upload():
    response.view = 'generic.' + request.extension
    def POST(**vars):
        #return dict(file = dir(vars['data'].file))
        stream = vars['data'].file
        filename = vars['data'].filename
        file_id = db.bot_upload.insert(bot_id = vars['bot_id'],
                                       bot_file = db.bot_upload.bot_file.store(stream,filename=filename))
        return dict(file = file_id, filename = file_id.bot_file)
    return locals()

@cors_allow
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@cors_allow
@request.restful()
def authk():
    response.view = 'generic.' + request.extension
    def PUT(**vars):
        from gluon.tools import Auth
        #getting the login data
        email = vars['email']
        password = vars['password']
        #login instruction
        user = auth.login_bare(email,password)
        first_name = ''
        last_name = ''
        api_token = ''
        if user:
            first_name = user.first_name
            last_name = user.last_name
            api_token = user.api_token
        return dict(data = (api_token,first_name,last_name))
        #return dict(token = db((db.auth_user.email == email) & (db.auth_user.password == passcode)).select(db.auth_user.api_token,db.auth_use-r.first_name,db.auth_user.last_name))
        #return dict(token = db.auth_user(id = authuser.id).api_token)
    return locals()

@cors_allow
@request.restful()
def password_reset():
    response.view = 'generic.' + request.extension
    def GET(email):
        import base64
        import binascii
        import os
        #email libs
        import urllib
        import ssl
        import smtplib
        #from for the pass-key
        from hmac import compare_digest
        from random import SystemRandom
        from email.mime.text import MIMEText
        #generates a new random password key
        new_pswd = str(binascii.hexlify(os.urandom(3))).replace("'", "")
        #update of the password in the table
        db(db.auth_user.email == email).update(password=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(new_pswd)[0]))
        #sending an email
        user = 'no-reply@botprotec.com'
        pswd = 'n0replyn0reply'
        msg = MIMEText("Your password has been reset, login with the password:" + new_pswd + ". \r\nWe strongly recommend you change your password on your account settings.\r\n\r\nBotPro")
        msg['Subject'] = "BotPro Account Password Reset"
        msg['From'] = user
        msg['To'] = email
        server = smtplib.SMTP_SSL('smtp.zoho.com', 465)
        server.login(user, pswd)
        server.sendmail(user, [email], msg.as_string())
        server.quit()
        return dict(data = 'ok')
    return locals()

@cors_allow
@request.restful()
def user():
    response.view = 'generic.' + request.extension
    def GET(email):
        #this function is only for verificaction of user existance
        return dict(count = db(db.auth_user.email == email).count())
    def PUT(**vars):
        #imports
        import datetime
        import base64
        import binascii
        import os
        from hmac import compare_digest
        from random import SystemRandom
        #generates a token
        token = str(binascii.hexlify(os.urandom(15))).replace("'", "")
        isUniqueToken = False
        while isUniqueToken == False:
            if (db(db.auth_user.api_token == token).count() > 0):
                token = str(binascii.hexlify(os.urandom(15))).replace("'", "")
            else:
                isUniqueToken = True
        #inserts the new generated token
        #create a new user
        generatedToken = token
        current_date = datetime.datetime.now()
        #user record is created
        db.auth_user.insert(
            email = vars['email'],
            first_name = vars['firstName'],
            last_name = vars['lastName'],
            password=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0]),
            #password=db.auth_user.password.validate(vars['password']),
            api_token = generatedToken,
            token_datetime = current_date)
        #return dict(token = db(db.auth_user.email == userData.first_name).select(db.auth_user.api_token))
        return dict(data = generatedToken)
    return locals()

@cors_allow
@request.restful()
def bot_variables_records():
    response.view = 'generic.' + request.extension
    def GET(bot_id,start_limit,end_limit):
        #getting the list of variables registered to the bot
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(data = db(db.bot_storage.bot_id == bot_id).select(db.bot_storage.storage_key, db.bot_storage.storage_owner, db.bot_storage.storage_value, limitby=(v_start_limit,v_end_limit)))
    return locals()

@cors_allow
@request.restful()
def bot_variables_recordcount():
    response.view = 'generic.' + request.extension
    def GET(bot_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.bot_storage.bot_id == bot_id).count())
    return locals()

@cors_allow
@request.restful()
def bot_variables():
    response.view = 'generic.' + request.extension
    def GET(bot_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.bot_storage.bot_id == bot_id).select(db.bot_storage.storage_key, distinct=True))
    return locals()

@cors_allow
@request.restful()
def bot_conversations():
    response.view = 'generic.' + request.extension
    def GET(bot_id,start_limit,end_limit):
        #getting the logged chats with a bot, delimited by a number of data
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(data = db(db.conversation.bot_id == bot_id).select(db.conversation.id, db.conversation.storage_owner, db.conversation.ctype, db.conversation.ccontent, db.conversation.message_date,db.conversation.message_time,db.conversation.origin, db.conversation.medium, db.conversation.content_type, limitby=(v_start_limit,v_end_limit)))
    return locals()

@cors_allow
@request.restful()
def bot_conversations_contact():
    response.view = 'generic.' + request.extension
    def GET(bot_id,storage_owner,start_limit,end_limit):
        #getting the logged chats with a bot, delimited by a number of data
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(data = db(db.conversation.bot_id == bot_id, db.conversation.storage_owner == storage_owner).select(db.conversation.id, db.conversation.storage_owner, db.conversation.ctype, db.conversation.ccontent, limitby=(v_start_limit,v_end_limit)))
    return locals()

@cors_allow
@request.restful()
def bot_conversations_recordcount():
    response.view = 'generic.' + request.extension
    def GET(bot_id):
        #getting the number of logged messages that a bot has
        return dict(data = db(db.conversation.bot_id == bot_id).count())
    return locals()

@cors_allow
@request.restful()
def website_connector():
    response.view = 'generic.' + request.extension
    def PUT(**vars):
        #getting the parameters
        bot_id = vars['bot_id']
        website = vars['website']
        #generates a random token for identifying a unique connection
        #imports
        import base64
        import binascii
        import os
        from hmac import compare_digest
        from random import SystemRandom
        #generates a token
        token = str(binascii.hexlify(os.urandom(15))).replace("'", "")
        isUniqueToken = False
        while isUniqueToken == 'hello':
            if (db(db.website_token.token == token).count() > 0):
                token = str(binascii.hexlify(os.urandom(15))).replace("'", "")
            else:
                isUniqueToken = True
        #inserts the new generated token
        db.website_token.insert(
            bot_id = bot_id,
            website = website,
            token = token)
        return dict(WebToken = token)
    #Update method
    def POST(**vars):
        #getting the parameters
        bot_id = vars['bot_id']
        website = vars['website']
        token = vars['token']
        db(db.website_token.token == token).update(website = website)
        return dict()
    #Delete method
    def DELETE(**vars):
        #getting the parameters
        bot_id = vars['bot_id']
        token = vars['token']
        #when a bot is deleted the same method is called with token parameter = 0
        if (token == 0):
            db(db.website_token.bot_id == bot_id).delete()
        else:
            #in any other case the connector is deleted from the table where the token value matches
            db(db.website_token.token == token).delete()
        return dict()
    return locals()

@cors_allow
@request.restful()
def bot_register():
    response.view = 'generic.' + request.extension
    def GET(bot_id, register_id, **vars):
        bot = db.bot(id = bot_id)
        connector = bot.connectors[int(register_id)]
        if connector['type'] == 'telegram':
            uri = 'https://api.telegram.org/bot%s/%s' % (connector['token'], 'setWebhook')
            import requests
            res = requests.post(uri, json=dict(url=URL('webhook','hook',args=['telegram',bot.id], scheme='https', host=True)))
            return res.json()
        elif connector['type']== 'fb':
            pass
        return dict()
    def DELETE(bot_id, register_id, **vars):
        bot = db.bot(id = bot_id)
        connector = bot.connectors[int(register_id)]
        if connector['type'] == 'telegram':
            uri = 'https://api.telegram.org/bot%s/%s' % (connector['token'], 'deleteWebhook')
            import requests
            res = requests.post(uri, json=dict(url=URL('webhook','hook',args=['telegram',bot.id], scheme='https', host=True)))
            return res.json()
        elif connector['type'] == 'fb':
            pass
        return dict()
    return locals()


@cors_allow
@request.restful()
def bot_intent_recordcount():
    response.view = 'generic.' + request.extension
    def GET(bot_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.bot_intent.bot_id == bot_id).count())
    return locals()
@cors_allow
@request.restful()
def bot_intents():
    response.view = 'generic.' + request.extension
    def GET(bot_id,start_limit,end_limit):
        #getting all the intents per bot
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(intents = db(db.bot_intent.bot_id == bot_id).select(db.bot_intent.id, db.bot_intent.context_id, db.bot_intent.name, limitby=(v_start_limit,v_end_limit)))
    def PUT(**vars):
        #update of intent
        db(db.bot_intent.id == vars['id']).update(context_id = vars['context_id'],name = vars['name'])
        return dict(result = 'ok')
    def POST(**vars):
        #insert of intent
        db.bot_intent.insert(
            bot_id = vars['bot_id'],
            context_id = vars['context_id'],
            name = vars['name']
        )
        return dict(result = 'ok')
    def DELETE(**vars):
        #deletion of intent
        db(db.bot_intent.id == vars['id']).delete()
        return dict(result = 'ok')
    return locals()

#intent_context_example
#-----------------------
@cors_allow
@request.restful()
def intent_example_count():
    response.view = 'generic.' + request.extension
    def GET(intent_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.intent_context_example.intent_id == intent_id).count())
    return locals()
@cors_allow
@request.restful()
def intent_example():
    response.view = 'generic.' + request.extension
    def GET(intent_id,start_limit,end_limit):
        #getting all the intents per bot
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(examples = db(db.intent_context_example.intent_id == intent_id).select(db.intent_context_example.id, db.intent_context_example.intent_id, db.intent_context_example.example_text, limitby=(v_start_limit,v_end_limit)))
    def PUT(**vars):
        #update of intent
        db(db.intent_context_example.id == vars['id']).update(example_text = vars['example_text'], intent_id = vars['intent_id'])
        return dict(result = 'ok')
    def POST(**vars):
        #insert of intent
        db.intent_context_example.insert(
            intent_id = vars['intent_id'],
            example_text = vars['example_text']
        )
        return dict(result = 'ok')
    def DELETE(**vars):
        #deletion of intent
        db(db.intent_context_example.id == vars['id']).delete()
        return dict(result = 'ok')
    return locals()
#-----------------------

@cors_allow
@request.restful()
def bot_ai():
    response.view = 'generic.' + request.extension
    def POST(**vars):
        #creates the file for the ai engine
        import os
        bot_id = vars['bot_id']
        input_stream = vars['file_content']
        myfile = os.path.join('/home/rasa/rasa_nlu/data/examples/rasa/', 'Project_' + str(bot_id) + ".json")
        f = open(myfile,'w')
        f.write(input_stream)
        f.close()
        return dict(result = 'ok')
    return locals()
#-------------------------
@cors_allow
@request.restful()
def bot_ai_config():
    response.view = 'generic.' + request.extension
    def POST(**vars):
        def excute(cmd,fileName, overwrite = False):
            import subprocess
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
            output = ''
            while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    output = output + out
            myfile = os.path.join('/home/rasa/rasa_nlu/sample_configs/', fileName)
            if overwrite:
                f = open(myfile,'w')
            else:
                f = open(myfile,'a')
            f.write(output)
            f.close()
        #creates the file for the ai engine
        import os
        bot_id = vars['bot_id']
        input_stream = vars['file_content']
        myfile = os.path.join('/home/rasa/rasa_nlu/sample_configs/',
                              'Project_%s.json' %(bot_id))
        f = open(myfile,'w')
        f.write(input_stream)
        f.close()
        #Deletes older models
        excute('rm -rf /home/rasa/rasa_nlu/projects/Project_%s/*' % (bot_id),
               'Train_%s.log' % (bot_id),
               overwrite = True)
        #Trains and create newer model
        excute('python -m rasa_nlu.train -c /home/rasa/rasa_nlu/sample_configs/Project_%s.json' % (bot_id),
               'Train_%s.log' % (bot_id))
        #re-starting the ai system
        excute('sudo systemctl restart rasa',
               'Train_%s.log' % (bot_id))
        return dict(result = 'ok')
    return locals()
#-------------------------

@cors_allow
@request.restful()
def api():
    response.view = 'generic.' + request.extension
    def GET(*args, **vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns, args, vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status, parser.error)

    def POST(table_name, **vars):
        import json
        for key in vars.keys():
            if db[table_name][key].type == 'json':
                vars[key] = json.loads(vars[key])
                vars[key] = json.dumps(vars[key])
        result = db[table_name].validate_and_insert(**vars)
        patterns = 'auto'
        if table_name == "bot_context":
            table_name = table_name.replace('_','-')
        #raise Exception(vars)
        parser = db.parse_as_rest(patterns, [table_name, 'id', str(result.id)], vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status, parser.error)
        #return dict(content = db(db[table_name]._id == result.id).select(), errors = result.errors)
    def PUT(table_name,record_id,**vars):
        import json
        for key in vars.keys():
            if db[table_name][key].type == 'json':
                vars[key] = json.loads(vars[key])
        db(db[table_name]._id==record_id).update(**vars)
        patterns = 'auto'
        table_name = table_name.replace('_','-')
        parser = db.parse_as_rest(patterns, [table_name,'id', record_id], vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status, parser.error)
    def DELETE(table_name,record_id,**vars):
        if table_name != "bot":
            raise HTTP(405,"METHOD NOT ALLOWED")
        import json
        r = db(db[table_name]._id==record_id).delete()
        return dict(content=r)
        #return dict(content = db(db[table_name]._id == record_id).select())
    return locals()

@cors_allow
@request.restful()
def deleteContext():
    response.view = 'generic.' + request.extension
    def GET(context_id):
        def tryRecursiveDelete(contextid):
            context_childs=db(db.bot_context.parent_context==contextid).select(db.bot_context.id,db.bot_context.name)
            for child in context_childs:
                if(db(db.bot_intent.context_id == child.id).count()>0):
                    return dict(data='error',cont=db(db.bot_context.id==child.id).select(db.bot_context.name),datos=db(db.bot_intent.context_id == child.id).select(db.bot_intent.name))
                return tryRecursiveDelete(child.id)
            if(db(db.bot_intent.context_id == contextid).count()>0):
                return dict(data='error',cont=db(db.bot_context.id==contextid).select(db.bot_context.name),datos=db(db.bot_intent.context_id == contextid).select(db.bot_intent.name))
            return dict(data = 'ok')
        def recursiveDelete(contextid):
            context_childs=db(db.bot_context.parent_context==contextid).select(db.bot_context.id,db.bot_context.name)
            for child in context_childs:
                recursiveDelete(child.id)
            db(db.bot_context.id==contextid).delete()
            return dict(data='ok')
            #intent_ids = db(db.bot_intent.context_id == child.id).select(db.bot_intent.id)
            #for intent_id in intent_ids:
            #    db(db.intent_context_example.intent_id==intent_id.id).delete()
            #db(db.bot_intent.context_id == child.id).delete()
        #intent_ids = db(db.bot_intent.context_id == context_id).select(db.bot_intent.id)
        #for intent_id in intent_ids:
        #    db(db.intent_context_example.intent_id==intent_id.id).delete()
        #db(db.bot_intent.context_id == context_id).delete()
        #db(db.bot_context.parent_context==context_id).delete()
        #db(db.bot_context.id==context_id).delete()
        #return dict(data = 'ok')
        response=tryRecursiveDelete(context_id)
        if(response!=dict(data='ok')):
            return response
        return recursiveDelete(context_id)
    return locals()

@cors_allow
@request.restful()
def changeContextName():
    import json
    response.view = 'generic.' + request.extension
    def GET(context_id,newName):
        respuesta=''
        contexts=db(db.bot_context.id==context_id).select(db.bot_context.name, db.bot_context.context_json)
        for context in contexts:
            respuesta=str(json.dumps(context.context_json)).replace('{"'+context.name+"\":",'{"'+newName+"\":")
        db(db.bot_context.id==context_id).update(name=newName,context_json=json.loads(respuesta))
        return dict(data=newName,cont=respuesta)
    return locals()

@cors_allow
@request.restful()
def existsContextName():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid,name):
        return dict(cont=db((db.bot_context.bot_id==botid)&(db.bot_context.name==name)).count())
    return locals()
@cors_allow
@request.restful()
def existsIntentName():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid,name):
        return dict(cont=db((db.bot_intent.bot_id==botid)&(db.bot_intent.name==name)).count())
    return locals()
@cors_allow
@request.restful()
def deleteMessengerConnector():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid,token):
        respuesta=''
        listconnectors=db(db.bot.id==botid).select(db.bot.connectors)
        connectors=listconnectors[0]['connectors']
        for connector in connectors:
            if(connector['type']=='messenger'):
                connectors.remove(connector)
        respuesta=connectors
        db(db.bot.id==botid).update(connectors=respuesta)
        return dict(cont='ok')
    return locals()
@cors_allow
@request.restful()
def deleteTelegramConnector():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid,token):
        respuesta=''
        listconnectors=db(db.bot.id==botid).select(db.bot.connectors)
        connectors=listconnectors[0]['connectors']
        for connector in connectors:
            if(connector['type']=='telegram'):
                connectors.remove(connector)
        respuesta=connectors
        db(db.bot.id==botid).update(connectors=respuesta)
        return dict(cont='ok')
    return locals()
@cors_allow
@request.restful()
def getBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid):
        respuesta=db(db.bot.id==botid).select(db.bot.ai_configured)
        return dict(cont=respuesta[0].ai_configured)
    return locals()
@cors_allow
@request.restful()
def setBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid):
        respuesta=''
        import requests
        params = (('q', 'hola'),('project', 'Project_'+ str(botid)))
        response = requests.get('http://localhost:5000/parse', params=params)
        if(str(response).split('[')[1].split(']')[0]=='200'):
            respuesta='ok'
            algo=db(db.bot.id==botid).update(ai_configured=True)
        else:
            respuesta=str(response)
            db(db.bot.id==botid).update(ai_configured=False)
        return dict(cont=respuesta)
    return locals()
@cors_allow
@request.restful()
def setFalseBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid):
        respuesta='ok'
        db(db.bot.id==botid).update(ai_configured=False)
        return dict(cont=respuesta)
    return locals()
@cors_allow
@request.restful()
def getTrainLog():
    import json
    response.view = 'generic.' + request.extension
    def GET(botid):
        respuesta='ok'
        try:
            fi=open('/home/rasa/rasa_nlu/sample_configs/Train_'+botid+'.log','r')
            return dict(cont=str(fi.read()))
        except:
            return dict(cont='there is not a logfile. You have never train this bot!')
    return locals()
@cors_allow
@request.restful()
def sendMessageToMesseger():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId,clientId,message):
        def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'chatCenter'
                import datetime
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
        def r(envelope):
            import requests
            tok=''
            connectors=db(db.bot.id==botId).select(db.bot.connectors)
            for conn in connectors[0].connectors:
                if(conn['type']=='messenger'):
                    tok=conn['token']
            uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token =tok)
            resu = requests.post(uri, json=envelope)
            return resu
        respuesta=r(dict(recipient = dict(id = clientId),message = dict(text = message)))
        log_conversation(clientId, message, botId, 'sent','text')
        return dict(cont=str(respuesta))
    return locals()
@cors_allow
@request.restful()
def sendMessageToTelegram():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId,clientId,message):
        def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'chatCenter'
                import datetime
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
        def r(method , envelope):
            import requests
            tok=''
            connectors=db(db.bot.id==botId).select(db.bot.connectors)
            for conn in connectors[0].connectors:
                if(conn['type']=='telegram'):
                    tok=conn['token']
            uri = 'https://api.telegram.org/bot{key}/{method}'.format(key = tok,method = method)
            resu = requests.post(uri, json=envelope)
            return resu
        respuesta=r('sendMessage', dict(chat_id = clientId,text = message))
        log_conversation(clientId, message, botId, 'sent','text')
        return dict(cont=str(respuesta))
    return locals()
@cors_allow
@request.restful()
def endChatCenter():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId,clientId):
        def log_conversation(chat_id, chat_text, bot, type,content_type):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'chatCenter'
                import datetime
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
        log_conversation(clientId, 'end by chatcenter', botId, 'sent','text')
        resp=db((db.conversation.bot_id==botId)&(db.conversation.storage_owner==clientId))
        respuesta=resp.update(need_chat_center=False)
        return dict(cont=str(respuesta))
    return locals()
@cors_allow
@request.restful()
def checkNeedChatCenter():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId):
        respuesta =[]
        resp=db(db.conversation.bot_id==botId)
        needchat=resp.select(db.conversation.need_chat_center,db.conversation.storage_owner, distinct=True)
        for need in needchat:
            contactid=need['storage_owner']
            needchat=need['need_chat_center']
            respuesta.append(dict(owner = contactid,chatcenter = needchat))
        return dict(cont=(respuesta))
    return locals()
@cors_allow
@request.restful()
def getAiRequests():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId):
        respuesta =[]
        resp=db(db.ai_request.bot_id==botId)
        requests=resp.select(db.ai_request.status,
                             db.ai_request.storage_owner,
                             db.ai_request.request_date,
                             db.ai_request.request_time,
                             db.ai_request.medium,
                             db.ai_request.ccontent,
                             db.ai_request.ai_response)
        for request in requests:
            respuesta.append(dict(owner = request['storage_owner'],
                                  status = request['status'],
                                  date=request['request_date'],
                                  time=request['request_time'],
                                  medium=request['medium'],
                                  content=request['ccontent'],
                                  ai_response=request['ai_response']
                                 ))
        return dict(cont=(respuesta))
    return locals()
@cors_allow
@request.restful()
def sendMessageToBroadcast():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId,message):
        def log_conversation(chat_id, chat_text, bot, type,content_type,medi,sta):
                msg_origin = 'client'
                if (type == 'sent'):
                    msg_origin = 'chatCenter'
                import datetime
                current_date = datetime.datetime.now()
                current_time = datetime.datetime.now().time()
                db.conversation.insert(bot_id = bot,
                                       storage_owner = chat_id,
                                       ctype = type,
                                       ccontent = chat_text,
                                       message_date = current_date,
                                       message_time = current_time,
                                       origin = msg_origin,
                                       medium = medi,
                                       content_type = content_type,
                                      need_chat_center=sta)
        def r_telegram(method , envelope):
            import requests
            tok=''
            connectors=db(db.bot.id==botId).select(db.bot.connectors)
            for conn in connectors[0].connectors:
                if(conn['type']=='telegram'):
                    tok=conn['token']
            uri = 'https://api.telegram.org/bot{key}/{method}'.format(key = tok,method = method)
            resu = requests.post(uri, json=envelope)
            return resu
        def r_messenger(envelope):
            import requests
            tok=''
            connectors=db(db.bot.id==botId).select(db.bot.connectors)
            for conn in connectors[0].connectors:
                if(conn['type']=='messenger'):
                    tok=conn['token']
            uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token =tok)
            resu = requests.post(uri, json=envelope)
            return resu
        #respuesta=r_messenger(dict(recipient = dict(id = clientId),message = dict(text = message)))
        #respuesta=r('sendMessage', dict(chat_id = 'Broadcast',text = message))
        users = db((db.conversation.bot_id==botId)&(db.conversation.medium=='telegram')).select(db.conversation.storage_owner,distinct=True)
        log_conversation('Broadcast', message, botId, 'sent','text','broadcast',True)
        for user in users:
            r_telegram('sendMessage', dict(chat_id = user.storage_owner,text = message))
            log_conversation(user.storage_owner,message,botId,'sent','text','telegram',False)
        users_ms = db((db.conversation.bot_id==botId)&(db.conversation.medium=='messenger')).select(db.conversation.storage_owner,distinct=True)
        for user in users_ms:
            r_messenger(dict(recipient = dict(id = user.storage_owner),message = dict(text = message)))
            log_conversation(user.storage_owner,message,botId,'sent','text','messenger',False)
        return dict(cont='end broadcast')
    return locals()
@cors_allow
@request.restful()
def getStatistics():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId, start , end):
        telegram_Total=-1
        messenger_Total=-1
        website_Total=-1
        checkpoints=[]
        if(start=='0'):
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')).count()
            che=db((db.bot_checkpoint.bot_id==botId)).select(db.bot_checkpoint.checkpoint_name)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)).count()
                checkpoints.append(dict(name=c.checkpoint_name,val=val))
        elif(start=='1'):
            import datetime
            current_date = datetime.datetime.now()
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram') & (db.conversation.message_date==current_date)).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')& (db.conversation.message_date==current_date)).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')& (db.conversation.message_date==current_date)).count()
            che=db((db.bot_checkpoint.bot_id==botId)& (db.bot_checkpoint.checkpoint_date==current_date)).select(db.bot_checkpoint.checkpoint_name)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)&
                       (db.bot_checkpoint.checkpoint_date==current_date)).count()
                checkpoints.append(dict(name=c.checkpoint_name,val=val))
        else:
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')
                              & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')
                              & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')
                            & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).count()
            che=db((db.bot_checkpoint.bot_id==botId)
                  & (db.bot_checkpoint.checkpoint_date>=start)& (db.bot_checkpoint.checkpoint_date<=end)).select(db.bot_checkpoint.checkpoint_name)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)
                      & (db.bot_checkpoint.checkpoint_date>=start)& (db.bot_checkpoint.checkpoint_date<=end)).count()
                checkpoints.append(dict(name=c.checkpoint_name,val=val))
        return dict(telegram_t=telegram_Total,messenger_t=messenger_Total,website_t=website_Total, start=start,end=end,check=checkpoints)
    return locals()
@cors_allow
@request.restful()
def botClone():
    import json
    response.view = 'generic.' + request.extension
    def GET(botId,name,full):
        cnt=[]
        r=db(db.bot.id==botId).select(db.bot.bot_language,db.bot.picture)
        newBotId=db.bot.insert(name=name,
                            bot_language=r[0].bot_language,
                           picture=r[0].picture)
        contexts=db(db.bot_context.bot_id==botId).select(db.bot_context.ALL)
        for context in contexts:
            intents=db(db.bot_intent.context_id==context.id).select(db.bot_intent.ALL)
            newContextId=db.bot_context.insert(bot_id=newBotId,parent_context=context.parent_context,
                                               isdefault=context.isdefault,name=context.name,
                                               context_json=context.context_json)
            cnt.append(dict(new=newContextId, old=context.id))
            for intent in intents:
                newIntentId=db.bot_intent.insert(bot_id=newBotId,context_id=newContextId,name=intent.name)
                if(full==True):
                    examples=db(db.intent_context_example.intent_id==intent.id).select(db.intent_context_example.ALL)
                    for example in examples:
                        db.intent_context_example.insert(intent_id=newIntentId,example_text=example.example_text)
        for c in cnt:
            db((db.bot_context.bot_id==newBotId)&(db.bot_context.parent_context==c['old'])).update(parent_context=c['new'])
        return dict(cont=(r),cn=contexts,inte=intents,act=cnt,newbot=newBotId)
    return locals()
@cors_allow
@request.restful()
def apiVariables():
    import json
    response.view = 'generic.' + request.extension
    def POST(**vars):
        import json
        r=''
        h=json.loads(vars['variables'])
        botId=vars['botid']
        clientId=vars['clientid']
        for key,value in h.items():
            db.bot_storage.insert(bot_id = botId,
                                       storage_owner = clientId,
                                       storage_key = key,
                                       storage_value = value)
        return dict(status= 'ok',cliente=clientId,bot=botId)
    return locals()
@cors_allow
@request.restful()
def apiPhantomContext():
    import json
    response.view = 'generic.' + request.extension
    def POST(**vars):
        import json
        h=json.loads(vars['jsonContext'])
        botId=vars['botid']
        clientId=vars['clientid']
        name=vars['name']
        db.bot_phantom_context.insert(bot_id = botId,storage_owner = clientId,context_json = (h),name=name,flow_position=0)
        return dict(context= str(h),cliente=clientId,bot=botId)
    return locals()
