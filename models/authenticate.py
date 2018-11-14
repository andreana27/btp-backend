# -*- coding: utf-8 -*-
def autenticado(f):
    def inner(*args):
        token=args[0]
        #search=db((db.auth_user.api_token==token)&(db.auth_user.enabled_access=='enable')).select(db.auth_user.id)
        if token==1:
             return True
        else:
            return False
    return f
#------------------------------------------------
def aviso(f1):
    search="";
    def inner1(*args):
        #response.view = 'generic.' + request.extension
        def GET(*args):
            #search=db((db.auth_user.api_token==token)&(db.auth_user.enabled_access=='enable')).select(db.auth_user.id)
            if True:
                f1
            else:
                raise Exception
            #return dict(data=args[0])
            return locals()
    return inner1
