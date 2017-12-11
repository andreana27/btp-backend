# -*- coding: utf-8 -*-
auth.settings.allow_basic_login = True
@cors_allow
@auth.requires(token_auth, requires_login=False)
def authk():
    response.view = 'generic.' + request.extension
    return dict(token = db.auth_user(id = auth.user.id).api_token)

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
