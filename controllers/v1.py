# -*- coding: utf-8 -*-

auth.settings.allow_basic_login = True
#@auth.requires(token_auth, requires_login=False)
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