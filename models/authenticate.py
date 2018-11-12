# -*- coding: utf-8 -*-
def aviso(f):
    def inner(*args, **kwargs):
        response.view = 'generic.' + request.extension
        def GET(*args):
            id=args[0]
            search=db((db.auth_user.api_token==args[0])&(db.auth_user.enabled_access=='enable')).select(db.auth_user.id)
            #var="user incorrecto"
            if search==None:
                search="No existe user"
            return dict(data = search)
        return locals()
        #f(*args, **kwargs)
        #print ("Se ejecuto %s" % f.__name__)
    return inner
