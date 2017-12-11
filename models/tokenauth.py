# -*- coding: utf-8 -*-
def token_auth():
    """Token Auth v1"""
    web2py_login = auth.user is not None
    token = request.vars.get('token')
    if auth.user is not None and token is None:
        import datetime
        import hashlib
        utcnow = datetime.datetime.utcnow()
        key = "BotPro%s%s%s" % (auth.user.id, auth.user.email, utcnow)
        token = hashlib.sha224(key).hexdigest()
        db(db.auth_user.id == auth.user.id).update(api_token = token,
                                                   token_datetime = utcnow)
    token_login = False
    if token is not None and auth.user is None:
        import datetime
        user = db((db.auth_user.api_token == token)&
                  (db.auth_user.token_datetime >= datetime.datetime.utcnow() - datetime.timedelta(minutes = 10))).select().first()
        if user:
            auth.user = user
            auth.user.update_record(token_datetime = datetime.datetime.utcnow())
            token_login = True
    return  web2py_login or token_login
