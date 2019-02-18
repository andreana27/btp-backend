# -*- coding: utf-8 -*-
#---------------------
auth.settings.allow_basic_login = True
#@auth.requires(token_auth, requires_login=False)
@cors_allow
@request.restful()
def upload():
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def POST(token,**vars):
        #return dict(file = dir(vars['data'].file))
        stream = vars['data'].file
        filename = vars['data'].filename
        file_id = db.bot_upload.insert(bot_id = vars['bot_id'],
                                       bot_file = db.bot_upload.bot_file.store(stream,filename=filename))
        return dict(file = file_id, filename = file_id.bot_file)
    return locals()

@cors_allow
@request.restful()
def bot_conversation_users():

    def GET(bot_id):
        users = set()
        for user in db(db.conversation.bot_id == bot_id).select():
            users.add(user.storage_owner)

        return response.json(users)

    return locals()

@cors_allow
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
#----------------------------------
@cors_allow
@request.restful()
def authk():
    #---
    response.view = 'generic.' + request.extension
    def PUT(**vars):
        from gluon.tools import Auth
        #getting the login data
        email = vars['email']
        password = vars['password']
        #policy
        #policy=db(db.auth_policies.id>0).select()
        #login instruction
        user = auth.login_bare(email,password)
        first_name = ''
        last_name = ''
        api_token = ''
        temporal=''
        date_password=''
        if user:
            first_name = user.first_name
            last_name = user.last_name
            api_token = user.api_token
            temporal=user.temporal_password
            date_password=user.password_change
        return dict(data = (api_token,first_name,last_name,temporal,date_password))
        #return dict(token = db((db.auth_user.email == email) & (db.auth_user.password == passcode)).select(db.auth_user.api_token,db.auth_use-r.first_name,db.auth_user.last_name))
        #return dict(token = db.auth_user(id = authuser.id).api_token)
    return locals()
#--------------------------------------
@cors_allow
@request.restful()
def user_filters():
    response.view = 'generic.' + request.extension
    #@decora('User Manager')
    def GET(token,id,name):
        datos=[]
        search=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_value.like('%'+name+'%', case_sensitive=False))&(db.bot_storage.storage_key=='fb_username')).select(db.bot_storage.storage_owner,db.bot_storage.storage_value,distinct=True)
        i=0
        for owner in search:
            searchpic=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_owner==owner.storage_owner)&(db.bot_storage.storage_key=='fb_profile_pic')).select(db.bot_storage.storage_owner,db.bot_storage.storage_value,distinct=True).first()
            if searchpic:
                datos.insert(i,[owner.storage_owner,owner.storage_value,searchpic.storage_value])
                i=i+1
        return dict(data=datos)
        '''searchpic=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_key=='fb_profile_pic')).select(db.bot_storage.storage_owner,db.bot_storage.storage_value,distinct=True)
        return dict(data=search,foto=searchpic)'''
    return locals()
#-----------decoradores---------------
def decora(valor):
    def decorador_put(f):
        def inner(*args,**kwargs):
            token=args[0]
            #------------------------------
            searchUser=db((db.auth_user.api_token==token)&(db.auth_user.enabled_access=='enable')).select().first()
            if searchUser:#found
                #search Role
                searchRole=db((db.auth_membership.user_id==searchUser.id)).select()
                #rolenum=''
                for cosa in searchRole:
                    #rolenum=rolenum+" "+str(int(cosa.group_id))
                    if searchRole:
                        functionality=db((db.auth_functionality.role_id==int(cosa.group_id))&(db.auth_functionality.feature_id==db.auth_feature.id)).select()#.first()
                        try:
                            if functionality:
                                for nombre in functionality:
                                    if str(nombre.auth_feature.feature_name)==valor:
                                        return f(*args,**kwargs)
                            #else:
                        except:
                            raise HTTP(401)
                    else:
                        raise HTTP(401)
            else:
                raise HTTP(401)
            #----------------------------
        return inner
    return decorador_put

@cors_allow
@request.restful()
def feature_decorador():
    response.view = 'generic.' + request.extension
    @decorator_of_test
    def GET(token,name):
        return dict(info="ok")
    return locals()
#-----------update 02/01/2019---------
'''@cors_allow
@request.restful()
def feedapi():
    response.view = 'generic.' + request.extension
    def POST(token,botid,owner,var,value):
        save_data=db.bot_storage.insert(bot_id=botid,storage_owner=owner,storage_key=var,storage_value=value)
        return dict(result=save_data)
    return locals()'''

@cors_allow
@request.restful()
def qualificationkey():
    response.view = 'generic.' + request.extension
    def GET(key,namekey,key_update,namekey_update):
        resultado=0
        get_owner=db((db.bot_storage.storage_key == key)&(db.bot_storage.storage_value==namekey)).select(
                  db.bot_storage.storage_owner,db.bot_storage.bot_id)
        if get_owner:
            for owner in get_owner:
                 resultadoactual=db.bot_storage.update_or_insert((db.bot_storage.storage_owner == owner.storage_owner)&
                                                    (db.bot_storage.storage_key ==key_update),
                                                  storage_owner = owner.storage_owner,
                                                  bot_id = owner.bot_id,
                                                  storage_key=key_update,
                                                  storage_value=namekey_update)
            resultado=1
        return dict(data=resultado)
    return locals()
#------Users update 29/10/2018--------
def count_users():
    response.view = 'generic.' + request.extension
    #@decorator_back_('User Manager')
    def GET(token,**vars):
        #ids = vars['id']
        #return dict(data = db(db.auth_user.id == bot_id).select())
        return dict(count = db(db.auth_user.id>0).count())
    return locals()
@cors_allow
@request.restful()
def auth_users():
    response.view = 'generic.' + request.extension
    @decora('User Manager')
    def POST(token,**vars):
        #ids = vars['id']
        #return dict(data = db(db.auth_user.id == bot_id).select())
        return dict(data = db(db.auth_user.id>0).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.email,db.auth_user.enabled_access))
    return locals()
@cors_allow
@request.restful()
def update_user():
    response.view = 'generic.' + request.extension
    @decora('User Manager')
    def PUT(token,**vars):
        import datetime
        respuesta=db(db.auth_user.id == vars['id']).update(first_name = vars['first_name'],last_name = vars['last_name'],email=vars['email'],enabled_access=vars['enabled_access'])
        if respuesta:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="actualizacion del usuario "+vars['first_name']+" "+vars['last_name']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)        
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def delete_user():
    response.view = 'generic.' + request.extension
    @decora('User Manager')
    def GET(token,id):
        db((db.auth_user.id==id)).delete()
        return dict(data ='ok')
    return locals()
#*****************Profile & policies*********************
@cors_allow
@request.restful()
def select_policiesALL():
    response.view = 'generic.' + request.extension
    @decora('User Policies')
    def POST(token):
        respuesta=db(db.auth_policies.id>0).select(orderby=db.auth_policies.id)
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def select_policies():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def POST(token,name):
        respuesta=db(db.auth_policies.policies_name==name).select().first()
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def update_policies():
    response.view = 'generic.' + request.extension
    @decora('User Policies')
    def POST(token,**vars):
        import datetime
        if vars['name']=='expirable-password':
             respuesta=db(db.auth_policies.policies_name==vars['name']).update(policies_active=vars['status'],date_end=vars['fecha2'])
             if respuesta:
                today = datetime.datetime.now()
                usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
                if usermaker:
                    descripcion="Actualizacion de la politica "+vars['name']+" con status:"+vars['status']+" y "+vars['fecha2']+" días para expirar"
                    seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        else:
            respuesta=db(db.auth_policies.policies_name==vars['name']).update(policies_active=vars['status'])
            if respuesta:
                today = datetime.datetime.now()
                usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
                if usermaker:
                    descripcion="Actualizacion de la politica "+vars['name']+" con status:"+vars['status']
                    seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        return dict(data = respuesta)
    return locals()
#................................
@cors_allow
@request.restful()
def update_passTemporal():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def PUT(token,**vars):
        import datetime
        current_date=datetime.datetime.now()
        password1=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0])
        respuesta=db(db.auth_user.api_token == token).update(password=password1,password_change=current_date,temporal_password=False)
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def update_profile():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def PUT(token,**vars):
        import datetime
        current_date=datetime.datetime.now()
        password1=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0])
        respuesta=db(db.auth_user.api_token == token).update(first_name = vars['first_name'],last_name = vars['last_name'],password=password1,password_change=current_date)
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def view_temporal():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def POST(token,**vars):
        respuesta=db(db.auth_user.api_token == token).select(db.auth_user.temporal_password).first()
        return dict(data = respuesta)
    return locals()
#----------------------------
@cors_allow
@request.restful()
def temp_password():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def PUT(token,**vars):
        import datetime
        current_date=datetime.datetime.now()
        password1=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0])
        respuesta=db(db.auth_user.api_token == token).update(password=password1,temporal_password=False,password_change=current_date)
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def expira_password():
    response.view = 'generic.' + request.extension
    @decora('User Profile')
    def PUT(token,**vars):
        import datetime
        current_date=datetime.datetime.now()
        password1=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0])
        respuesta=db(db.auth_user.api_token == token).update(password=password1,temporal_password=False,password_change=current_date)
        return dict(data = respuesta)
    return locals()
#***********Roles***********************
@cors_allow
@request.restful()
def create_role():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def GET(token,**vars):
        db.auth_group.insert(
            role = vars['role'],
            description = vars['description'])
        return dict(data = 'ok')
    return locals()
@cors_allow
@request.restful()
def add_user_role():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def GET(token,id):
        return dict(count = db(db.auth_membership.user_id == id).count())
    @decora('Role Manager')
    def POST(token,**vars):
        import datetime
        response='ok add'
        if(db((db.auth_membership.user_id == vars['iduser']) &(db.auth_membership.group_id == vars['idrol']) ).count()<1):
            user=db.auth_membership.insert(user_id = vars['iduser'],group_id = vars['idrol'])
            if user:
                today = datetime.datetime.now()
                usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="Agregar usuario ID"+vars['iduser']+" en el rol No. "+vars['idrol']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        else:
            response='user already exists'
        return dict(data = response)
    return locals()
@cors_allow
@request.restful()
def group_membership():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,id):#POST
        return dict(data = db((db.auth_user.id==db.auth_membership.user_id)&(db.auth_membership.group_id==id)).select(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name))
    return locals()
@cors_allow
@request.restful()
def select_roles():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,**vars):#POST
        return dict(data =db((db.auth_group.id>0)).select() )
    return locals()
@cors_allow
@request.restful()
def delete_Userinroles():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,**vars):
    #def GET(id,group):
        import datetime
        hola=db((db.auth_membership.user_id==vars['iduser'])&(db.auth_membership.group_id==vars['idrol'])).delete()
        if hola:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="Eliminacion del usuario con ID "+vars['iduser']+" del rol ID "+vars['idrol']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        return dict(data =hola)
    return locals()
@cors_allow
@request.restful()
def count_membership():
    response.view = 'generic.' + request.extension
    def GET(id):
        #return dict(data = db(db.auth_user.id == bot_id).select())
        return dict(count = db((db.auth_membership.user_id==db.auth_user.id)&(db.auth_group.id==db.auth_membership.group_id)&(db.auth_membership.group_id==id)).count())
    return locals()
@cors_allow
@request.restful()
def role():
    response.view = 'generic.' + request.extension
    def GET(role):
        #this function is only for verificaction of role existance
        return dict(count = db(db.auth_group.role == role).count())
    @decora('Role Manager')
    def PUT(token,**vars):
        #role record is created
        import datetime
        roleok=db.auth_group.insert(role = vars['role'],description = vars['description'],access_role = 'enable')
        if roleok:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="creacion del rol "+vars['role']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        #busqueda del rol
        search=db(db.auth_group.role == vars['role']).select(db.auth_group.id)
        return dict(data = search)
    return locals()
@cors_allow
@request.restful()
def update_role():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def PUT(token,**vars):
        import datetime
        actual=db(db.auth_group.id == vars['id']).update(role = vars['role'],description = vars['description'],access_role=vars['access_role'])
        if actual:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="Actualizacion de datos del rol "+vars['role']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        return dict(data = actual)
    return locals()
#***********Features********************
@cors_allow
@request.restful()
def add_feature():
    response.view = 'generic.' + request.extension
        #return dict(count = db(db.auth_group.role == role).count())
    @decora('Role Manager')
    def GET(token,name):
        response='ok add'
        if(db((db.auth_feature.feature_name == name) ).count()<1):
            db.auth_feature.insert(feature_name = name)
        else:
            response='user already exists'
        return dict(data = response)
    return locals()
@cors_allow
@request.restful()
def select_features():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,**vars):
        return dict(grid = db(db.auth_feature.id>0).select())
    return locals()
@cors_allow
@request.restful()
def select_functionality():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,id):#POST
        #return dict(data = db(db.auth_user.id == bot_id).select())
        return dict(data = db((db.auth_feature.id==db.auth_functionality.feature_id)&(db.auth_functionality.role_id==id)).select(db.auth_functionality.role_id,db.auth_functionality.feature_id,db.auth_feature.feature_name))
    return locals()
@cors_allow
@request.restful()
def add_functionality():
    response.view = 'generic.' + request.extension
        #return dict(count = db(db.auth_group.role == role).count())
    @decora('Role Manager')
    def POST(token,**vars):
        import datetime
        respuesta='ok add'
        if(db((db.auth_functionality.feature_id == vars['idfeature'])&(db.auth_functionality.role_id==vars['id']) ).count()<1):
            #insertar funcionalidad en el rol
            funcionok=db.auth_functionality.insert(feature_id =vars['idfeature'],role_id=vars['id'])
            if funcionok:
                today = datetime.datetime.now()
                usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
                if usermaker:
                    descripcion="creacion de permiso para modulo No. "+vars['idfeature']+" asignada al rol No. "+vars['id']
                    seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        else:
            respuesta='already exists'
        return dict(data = respuesta)
    return locals()
@cors_allow
@request.restful()
def delete_functionality():
    response.view = 'generic.' + request.extension
    @decora('Role Manager')
    def POST(token,**vars):
        import datetime
        hola=db((db.auth_functionality.role_id==vars['id'])&(db.auth_functionality.feature_id==vars['idfeature'])).delete()
        if hola:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==token)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="Eliminacion de la funcionalidad No. "+vars['idfeature']+" del rol No. "+vars['id']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        return dict(data =hola)
    return locals()
#---------------------------------------------------------
@cors_allow
@request.restful()
def table_name():
    response.view = 'generic.' + request.extension
    def GET(**vars):
        nombre=db.executesql('SELECT table_name FROM information_schema.tables WHERE table_schema= \'public\' AND table_type=\'BASE TABLE\';')
        return dict(grid=nombre)
    return locals()
#*************************Track*********************************************
@cors_allow
@request.restful()
def tracking_status():
    response.view = 'generic.' + request.extension
    @decora('Bot Tracking')
    def POST(token,id):#POST
        resultado=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_value<>None)&(db.bot_storage.storage_key<>None)&(db.bot_storage.storage_value<>"")&(db.bot_storage.storage_key<>"")).select(db.bot_storage.storage_key,distinct=True)
        return dict(content =resultado)
    return locals()
#----------------------------------------------------------
@cors_allow
@request.restful()
def password_reset():
    response.view = 'generic.' + request.extension
    #@decora('User Profile')
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
        db(db.auth_user.email == email).update(password=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(new_pswd)[0]),temporal_password=True)
        #sending an email
        user = 'no-reply@botprotec.com'
        pswd = 'n0replyn0reply'
        msg = MIMEText("Your password has been reset, login with the password:" + new_pswd + ". \r\nWe strongly recommend you change your password on your account settings, because the password provided is temporary.\r\n\r\nBotPro")
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
    #@decora('User Manager')
    def POST(email):
        #this function is only for verificaction of user existance
        return dict(count = db(db.auth_user.email == email).count())
    @decora('User Manager')
    def PUT(token,**vars):
        #imports
        import datetime
        import base64
        import binascii
        import os
        from hmac import compare_digest
        from random import SystemRandom
        tokenmaker=token
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
        user=db.auth_user.insert(
            email = vars['email'],
            first_name = vars['firstName'],
            last_name = vars['lastName'],
            password=str(CRYPT(digest_alg='pbkdf2(1000,20,sha512)',salt=True)(vars['password'])[0]),
            #password=db.auth_user.password.validate(vars['password']),
            api_token = generatedToken,
            token_datetime = current_date,
            enabled_access='enable',
            password_change=current_date)
        #-----------------------------------------------------------------------------------------------
        if user:
            today = datetime.datetime.now()
            usermaker=db((db.auth_user.api_token==tokenmaker)).select(db.auth_user.email).first()
            if usermaker:
                descripcion="creacion del usuario "+vars['firstName']+" "+vars['lastName']
                seleccion=db.history_user.insert(action_date=today,responsible_user=usermaker.email,description=descripcion)
        #return dict(token = db(db.auth_user.email == userData.first_name).select(db.auth_user.api_token))
        return dict(data = generatedToken)
    return locals()

@cors_allow
@request.restful()
def bot_variables_records():
    response.view = 'generic.' + request.extension
    @decora('Bot Data Manager')
    def GET(token,bot_id,start_limit,end_limit):
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
    @decora('Bot Management')
    def GET(token,bot_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.bot_storage.bot_id == bot_id).select(db.bot_storage.storage_key, distinct=True))
    return locals()

@cors_allow
@request.restful()
def bot_conversations():
    response.view = 'generic.' + request.extension
    @decora('Bot Chat Center')
    def GET(token,bot_id,start_limit,end_limit):
        #getting the logged chats with a bot, delimited by a number of data
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(data = db(db.conversation.bot_id == bot_id).select(db.conversation.id, db.conversation.storage_owner, db.conversation.ctype, db.conversation.ccontent, db.conversation.message_date,db.conversation.message_time,db.conversation.origin, db.conversation.medium, db.conversation.content_type, limitby=(v_start_limit,v_end_limit), orderby=db.conversation.id))
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
    @decora('Bot Chat Center')
    def GET(token,bot_id):
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
    @decora('Bot Management')
    def DELETE(tokens,**vars):
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
    @decora('Bot Intents Manager')
    def GET(token,bot_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.bot_intent.bot_id == bot_id).count())
    return locals()
@cors_allow
@request.restful()
def bot_intents():
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,bot_id,start_limit,end_limit):
        #getting all the intents per bot
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(intents = db(db.bot_intent.bot_id == bot_id).select(db.bot_intent.id, db.bot_intent.context_id, db.bot_intent.name, limitby=(v_start_limit,v_end_limit)))
    @decora('Bot Intents Manager')
    def PUT(token,**vars):
        #update of intent
        db(db.bot_intent.id == vars['id']).update(context_id = vars['context_id'],name = vars['name'])
        return dict(result = 'ok')
    @decora('Bot Intents Manager')
    def POST(token,**vars):
        #insert of intent
        db.bot_intent.insert(
            bot_id = vars['bot_id'],
            context_id = vars['context_id'],
            name = vars['name']
        )
        return dict(result = 'ok')
    @decora('Bot Intents Manager')
    def DELETE(token,**vars):
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
    @decora('Bot Intents Manager')
    def GET(token,intent_id):
        #getting the list of variables registered to the bot
        return dict(data = db(db.intent_context_example.intent_id == intent_id).count())
    return locals()
@cors_allow
@request.restful()
def intent_example():
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,intent_id,start_limit,end_limit):
        #getting all the intents per bot
        v_start_limit = int(start_limit)
        v_end_limit = int(end_limit)
        return dict(examples = db(db.intent_context_example.intent_id == intent_id).select(db.intent_context_example.id, db.intent_context_example.intent_id, db.intent_context_example.example_text, limitby=(v_start_limit,v_end_limit)))
    @decora('Bot Intents Manager')
    def PUT(token,**vars):
        #update of intent
        db(db.intent_context_example.id == vars['id']).update(example_text = vars['example_text'], intent_id = vars['intent_id'])
        return dict(result = 'ok')
    @decora('Bot Intents Manager')
    def POST(token,**vars):
        #insert of intent
        db.intent_context_example.insert(
            intent_id = vars['intent_id'],
            example_text = vars['example_text']
        )
        return dict(result = 'ok')
    @decora('Bot Intents Manager')
    def DELETE(token,**vars):
        #deletion of intent
        db(db.intent_context_example.id == vars['id']).delete()
        return dict(result = 'ok')
    return locals()
#-----------------------
@cors_allow
@request.restful()
def bot_ai():
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def POST(token,**vars):
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
    @decora('Bot Intents Manager')
    def POST(token,**vars):
        def excute(cmd,fileName, overwrite = False):
            import subprocess
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
            output = '>>> %s\n' % (cmd)
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
        import json
        import os
        data = dict()
        data["rasa_nlu_data"] = dict()
        data["rasa_nlu_data"]["common_examples"] = []
        data["rasa_nlu_data"]["regex_features"] = []
        data["rasa_nlu_data"]["entity_synonyms"] = []
        intents = db(db.bot_intent.bot_id == vars['bot_id']).select()
        for intent in intents:
            examples = db(db.intent_context_example.intent_id == intent.id).select()
            for example in examples:
                data["rasa_nlu_data"]["common_examples"].append(dict(text = example.example_text, intent = intent.name, entities=[]))
        to_save = json.dumps(data)
        bot_id = vars['bot_id']
        input_stream = vars['file_content']
        myfile = os.path.join('/home/rasa/rasa_nlu/data/examples/rasa/', 'Project_' + str(bot_id) + ".json")
        f = open(myfile,'w')
        f.write(to_save)
        f.close()
        #creates the file for the ai engine
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
        excute('python -m rasa_nlu.train -c /home/rasa/rasa_nlu/sample_configs/Project_%s.json -d /home/rasa/rasa_nlu/data/examples/rasa/Project_%s.json --path /home/rasa/rasa_nlu/projects/ --project Project_%s' % (bot_id, bot_id, bot_id),
               'Train_%s.log' % (bot_id))
        #re-starting the ai system
        excute('sudo systemctl restart rasa',
               'Train_%s.log' % (bot_id))
        import time
        time.sleep(10)        #Wait for rasa to restart
        return dict(result = 'ok')
    return locals()
#--------------API----------------------
@cors_allow
@request.restful()
def api():
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns, args, vars)
        if parser.status == 200:
            return dict(content=parser.response)#dict(content=("hola token:"+args[0]+" "+token))#
        else:
            raise HTTP(parser.status, parser.error)
    @decora('Bot Management')
    def POST(token,table_name, **vars):
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
    @decora('Bot Management')
    def PUT(token,table_name,record_id,**vars):
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
    @decora('Bot Management')
    def DELETE(token,table_name,record_id,**vars):
        if table_name != "bot":
            raise HTTP(405,"METHOD NOT ALLOWED")
        import json
        r = db(db[table_name]._id==record_id).delete()
        return dict(content=r)
        #return dict(content=token)
        ##return dict(content = db(db[table_name]._id == record_id).select())
    return locals()

@cors_allow
@request.restful()
def deleteContext():
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,context_id):
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
    @decora('Bot Management')
    def GET(token,context_id,newName):
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
    @decora('Bot Management')
    def GET(token,botid,name):
        return dict(cont=db((db.bot_context.bot_id==botid)&(db.bot_context.name==name)).count())
    return locals()

def decorador1(f):
    def inner(*args):
        token=args[0]
            #------------------------------
        return dict(cont=("valor: "+token))
            #----------------------------
    return inner
@cors_allow
@request.restful()
def existsIntentName():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,botid,name):
        return dict(cont=db((db.bot_intent.bot_id==botid)&(db.bot_intent.name==name)).count())
    return locals()
#--------------------------------------
@cors_allow
@request.restful()
def deleteMessengerConnector():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,botid,apitoken):
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
    @decora('Bot Management')
    def GET(token,botid,apitoken):
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
#------------------------------------------    
@cors_allow
@request.restful()
def getBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,botid):
        respuesta=db(db.bot.id==botid).select(db.bot.ai_configured)
        return dict(cont=respuesta[0].ai_configured)
    return locals()
#--------------------------------------
@cors_allow
@request.restful()
def getBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,botid):
        respuesta=db(db.bot.id==botid).select(db.bot.ai_configured)
        return dict(cont=respuesta[0].ai_configured)
    return locals()
@cors_allow
@request.restful()
def setBotTrainStatus():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,botid):
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
    @decora('Bot Intents Manager')
    def GET(token,botid):
        respuesta='ok'
        db(db.bot.id==botid).update(ai_configured=False)
        return dict(cont=respuesta)
    return locals()
@cors_allow
@request.restful()
def getTrainLog():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,botid):
        respuesta='ok'
        try:
            fi=open('/home/rasa/rasa_nlu/sample_configs/Train_'+botid+'.log','r')
            return dict(cont=str(fi.read()))
        except:
            return dict(cont='there is not a logfile. You have never train this bot!')
    return locals()
@cors_allow
@request.restful()
def sendMessageToMessegerg():
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
def sendMessageToTelegramg():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Chat Center')
    def GET(token,botId,clientId,message):
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
def sendMessageToMesseger():
    response.view = 'generic.' + request.extension
    @decora('Bot Chat Center')
    def POST(token,**vars):
        #creates the file for the ai engine
        botId = vars['bot_id']
        message = vars['message']
        clientId=vars['clientid']
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
                                       content_type = content_type,
                                       need_chat_center=True)
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
        return dict(result = 'ok')
    return locals()
@cors_allow
@request.restful()
def sendMessageToTelegram():
    response.view = 'generic.' + request.extension
    def POST(**vars):
        #creates the file for the ai engine
        botId = vars['bot_id']
        message = vars['message']
        clientId=vars['clientid']
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
                                       content_type = content_type,
                                       need_chat_center=True)
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
        return dict(result = 'ok')
    return locals()
@cors_allow
@request.restful()
def endChatCenter():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Chat Center')
    def GET(token,botId,clientId):
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
    @decora('Bot Chat Center')
    def GET(token,botId):
        respuesta =[]
        resp=db((db.conversation.bot_id==botId) & (db.conversation.storage_owner==db.bot_storage.storage_owner)& (db.conversation.bot_id==db.bot_storage.bot_id)&(db.bot_storage.storage_key=="fb_username"))
        needchat=resp.select(db.conversation.need_chat_center,db.conversation.storage_owner,db.bot_storage.storage_value,distinct=db.conversation.storage_owner)
        if needchat:
            for need in needchat:
                contactid=need['conversation.storage_owner']
                needchat=need['conversation.need_chat_center']
                user=need['bot_storage.storage_value']
                fotos=db((db.bot_storage.storage_owner==contactid)&(db.bot_storage.storage_key=='fb_profile_pic')).select(db.bot_storage.storage_value).first()
                imagen="assets/images/person_64.png"
                if fotos:
                    imagen=fotos['bot_storage.storage_value']
                respuesta.append(dict(owner = contactid,chatcenter = needchat, userfb = user,imagen=imagen))
        else:
            resp=db(db.conversation.bot_id==botId)
            needchat=resp.select(db.conversation.need_chat_center,db.conversation.storage_owner, distinct=True)
            for need in needchat:
                contactid=need['storage_owner']
                needchat=need['need_chat_center']
                imagen=['assets/images/person_64.png']
                respuesta.append(dict(owner = contactid,chatcenter = needchat,imagen=imagen))
        return dict(cont=respuesta)
    return locals()
#-------------------------------------------------------------------------------------------------------------
@cors_allow
@request.restful()
def getAiRequests():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Intents Manager')
    def GET(token,botId):
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
    response.view = 'generic.' + request.extension
    @decora('Bot Chat Center')
    def POST(token,**vars):
        #creates the file for the ai engine
        botId = vars['bot_id']
        message = vars['message']
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
            return resu.text if resu != None else ''
        def r_messenger(envelope):
            import requests
            tok=''
            connectors=db(db.bot.id==botId).select(db.bot.connectors)
            for conn in connectors[0].connectors:
                if(conn['type']=='messenger'):
                    tok=conn['token']
            uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token =tok)
            resu = requests.post(uri, json=envelope)
            return resu.text if resu != None else ''
        #respuesta=r_messenger(dict(recipient = dict(id = clientId),message = dict(text = message)))
        #respuesta=r('sendMessage', dict(chat_id = 'Broadcast',text = message))
        users = db((db.conversation.bot_id==botId)&(db.conversation.medium=='telegram')).select(db.conversation.storage_owner,distinct=True)
        log_conversation('Broadcast', message, botId, 'sent','text','broadcast',True)
        for user in users:
            answer = r_telegram('sendMessage', dict(chat_id = user.storage_owner,text = message))
            log_conversation(user.storage_owner,message,botId,'sent','text','telegram',False)
            log_conversation(user.storage_owner,'broadcast status: %s' % (answer),botId,'sent','text','telegram',False)
        users_ms = db((db.conversation.bot_id==botId)&(db.conversation.medium=='messenger')).select(db.conversation.storage_owner,distinct=True)
        for user in users_ms:
            answer = r_messenger(dict(recipient = dict(id = user.storage_owner),message = dict(text = message)))
            log_conversation(user.storage_owner,message,botId,'sent','text','messenger',False)
            log_conversation(user.storage_owner,'broadcast status: %s' % (answer),botId,'sent','text','messenger',False)
        return dict(cont='end broadcast, %s messenger, %s telegram' % (len(users_ms), len(users)))
    return locals()
#-------------------------
@cors_allow
@request.restful()
def getTrackingTable2():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Tracking')
    def GET(token,botId,key,start,end):
        #horamin=db.conversation.message_time.min().with_alias('hora')
        from datetime import datetime, date, time, timedelta
        import calendar
        fechamin = db.bot_internal_storage.first_contact.min().with_alias('fecha')
        #row = db(db.bot_internal_storage.bot_id==botId).select(fechamin)
        #---------------------------------------------------------------------------------------------------
        Total_storage=len(db((db.bot_internal_storage.bot_id==botId)).select(db.bot_internal_storage.storage_owner,distinct=True))
        end=datetime.strptime(end, "%Y-%m-%d")+timedelta(days=1)
        #---------------------------------------------------------------------------------------------------
        storage=db((db.bot_internal_storage.bot_id==botId)&(db.bot_internal_storage.channel_id<>None)&
                (db.bot_storage.storage_key==key)& (db.bot_internal_storage.first_contact>=start)& 
                (db.bot_internal_storage.first_contact<=end)&
                (db.bot_internal_storage.storage_owner==db.bot_storage.storage_owner)&
                (db.bot_internal_storage.bot_id==db.bot_storage.bot_id)).select(db.bot_internal_storage.ALL,fechamin,db.bot_storage.storage_value,distinct=True,groupby=(db.bot_internal_storage.id,db.bot_storage.storage_value))
        return dict(Total=Total_storage,datos1=storage)
    return locals()
@cors_allow
@request.restful()
def insertNameAd():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Tracking')
    def PUT(token, **vars):
        actual=db((db.bot_internal_storage.bot_id == vars['idbot'])&(db.bot_internal_storage.ad_id==vars['idad'])&(db.bot_internal_storage.source_type=='ADS')).update(ad_name = vars['adname'])
        #-----------------------------------
        return dict(info=actual)
    return locals()

#---------------------------------------------------------
@cors_allow
@request.restful()
def deleteStartedButton():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token, bot_token):
        import httplib, urllib2,urllib
        url='https://graph.facebook.com/v2.6/me/thread_settings?access_token='+bot_token
        data = urllib.urlencode({'setting_type':'call_to_actions','thread_state':'new_thread'})
        headers = {"Content-type": "application/json"}
        payload = {'setting_type':'call_to_actions','thread_state':'new_thread'}
        request = urllib2.Request(url, data=data)
        request.get_method = lambda: 'DELETE' #'Delete pr Put'
        response = urllib2.urlopen(request)
        envio=response.read()
        #-----------------------------------
        return dict(token=envio)
    return locals()
@cors_allow
@request.restful()
def getStartedButton():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token, bot_token):
        import httplib, urllib
        parametros = urllib.urlencode({'setting_type':'call_to_actions','type':'No Auth','thread_state':'new_thread','call_to_actions':[{		'payload':'first contact bot'}]})
        sitio = urllib.urlopen("https://graph.facebook.com/v2.6/me/thread_settings?access_token="+bot_token, parametros)
        envio=sitio.read()
        return dict(token=envio)
    return locals()
#-------------------------------------------------------------------------------------------------------
@cors_allow
@request.restful()
def getTracking():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Tracking')
    def GET(token, botId,start,end):#(token, botId, start , end):
        from datetime import datetime, date, time, timedelta
        import calendar
        #---------------------------------------------------------------------------------------------------
        Total_storage=len(db((db.bot_internal_storage.bot_id==botId)).select(db.bot_internal_storage.storage_owner,distinct=True))
        end=datetime.strptime(end, "%Y-%m-%d")+timedelta(days=1)
        storage=db((db.bot_internal_storage.bot_id==botId)&(db.bot_internal_storage.channel_id<>None)& (db.bot_internal_storage.first_contact>=start)& (db.bot_internal_storage.first_contact<=end)).select(db.bot_internal_storage.channel_id,db.bot_internal_storage.ad_id,distinct=True)
        datos=[]
        canal=[]
        ad=[]
        ad_owner=[]
        porcent=[]
        for user in storage:
            usuarios=len(db((db.bot_internal_storage.bot_id==botId)&(db.bot_internal_storage.channel_id==user.channel_id)&(db.bot_internal_storage.ad_id==user.ad_id)).select(db.bot_internal_storage.storage_owner,distinct=True))
            if user.ad_id=="" or user.ad_id==None:
                user.ad_id="N/A"
            ad.append(user.ad_id)
            if user.channel_id!="":
                largo=len(user.channel_id.split(","))
                cad=user.channel_id.split(",")
                if largo==2:
                    ad_propio=user.channel_id.split(",")[1]
                else:
                    ad_propio='N/A'
            #--------------------------------------------------
            ad_owner.append(ad_propio)
            user.channel_id=user.channel_id.split(",")[0]
            canal.append(user.channel_id)
            datos.append(usuarios)
            porcentaje=((int(usuarios)*100)/int(Total_storage))
            porcent.append(porcentaje)
        return dict(Total_interStorage=Total_storage,buser=datos,anuncio=ad,adpropio=ad_owner,canalito=canal,pocentajeU=porcent)
    return locals()

#------------------------------------------------
@cors_allow
@request.restful()
def getStatistics():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Statistics')
    def GET(token,botId, start , end):
        telegram_Total=-1
        messenger_Total=-1
        website_Total=-1
        telegram_clients=-1
        messenger_clients=-1
        website_clients=-1
        checkpoints=[]
        if(start=='0'):
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')&(db.conversation.origin=='client')).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')&(db.conversation.origin=='client')).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')&(db.conversation.origin=='client')).count()
            che=db((db.bot_checkpoint.bot_id==botId)).select(db.bot_checkpoint.checkpoint_name,distinct=True)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)).count()
                clients=len(db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)).select(db.bot_checkpoint.storage_owner,distinct=True))
                checkpoints.append(dict(name=c.checkpoint_name,val=val,clients=clients))
            telegram_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')&(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
            messenger_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')&(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
            website_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')&(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
        elif(start=='1'):
            import datetime
            current_date = datetime.datetime.now()
            telegram_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')& (db.conversation.message_date==current_date)
                                    &(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
            messenger_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')& (db.conversation.message_date==current_date)
                                    &(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
            website_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')& (db.conversation.message_date==current_date)
                                    &(db.conversation.origin=='client')).select(db.conversation.storage_owner,distinct=True))
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram') & (db.conversation.message_date==current_date)&(db.conversation.origin=='client')).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')& (db.conversation.message_date==current_date)&(db.conversation.origin=='client')).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')& (db.conversation.message_date==current_date)&(db.conversation.origin=='client')).count()
            che=db((db.bot_checkpoint.bot_id==botId)& (db.bot_checkpoint.checkpoint_date==current_date)).select(db.bot_checkpoint.checkpoint_name,distinct=True)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)&
                       (db.bot_checkpoint.checkpoint_date==current_date)).count()
                clients=len(db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)&
                       (db.bot_checkpoint.checkpoint_date==current_date)).select(db.bot_checkpoint.storage_owner,distinct=True))
                checkpoints.append(dict(name=c.checkpoint_name,val=val,clients=clients))
        else:
            telegram_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')&(db.conversation.origin=='client')
                                    & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).select(db.conversation.storage_owner,distinct=True))
            messenger_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')&(db.conversation.origin=='client')
                                    & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).select(db.conversation.storage_owner,distinct=True))
            website_clients=len(db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')&(db.conversation.origin=='client')
                                    & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)).select(db.conversation.storage_owner,distinct=True))
            telegram_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='telegram')
                              & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)&(db.conversation.origin=='client')).count()
            messenger_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='messenger')
                              & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)&(db.conversation.origin=='client')).count()
            website_Total=db((db.conversation.bot_id==botId) & (db.conversation.medium=='website')
                            & (db.conversation.message_date>=start)& (db.conversation.message_date<=end)&(db.conversation.origin=='client')).count()
            che=db((db.bot_checkpoint.bot_id==botId)
                  & (db.bot_checkpoint.checkpoint_date>=start)& (db.bot_checkpoint.checkpoint_date<=end)).select(db.bot_checkpoint.checkpoint_name,distinct=True)
            for c in che:
                val=db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)
                      & (db.bot_checkpoint.checkpoint_date>=start)& (db.bot_checkpoint.checkpoint_date<=end)).count()
                checkpoints.append(dict(name=c.checkpoint_name,val=val,clients=clients))
                clients=len(db((db.bot_checkpoint.bot_id==botId)&(db.bot_checkpoint.checkpoint_name==c.checkpoint_name)
                      & (db.bot_checkpoint.checkpoint_date>=start)& (db.bot_checkpoint.checkpoint_date<=end)).select(db.bot_checkpoint.storage_owner,distinct=True))
        return dict(telegram_t=telegram_Total,messenger_t=messenger_Total,website_t=website_Total, start=start,end=end,check=checkpoints,
                    telegram_clients=telegram_clients,messenger_clients=messenger_clients,website_clients=website_clients)
    return locals()
@cors_allow
@request.restful()
def botClone():
    import json
    response.view = 'generic.' + request.extension
    @decora('Bot Management')
    def GET(token,botId,name,full):
        respss=''
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
                if(full=='true'):
                    respss='entroa full'
                    examples=db(db.intent_context_example.intent_id==intent.id).select(db.intent_context_example.ALL)
                    for example in examples:
                        db.intent_context_example.insert(intent_id=newIntentId,example_text=example.example_text)
        for c in cnt:
            db((db.bot_context.bot_id==newBotId)&(db.bot_context.parent_context==c['old'])).update(parent_context=c['new'])
            newjson=db((db.bot_context.bot_id==newBotId)&(db.bot_context.id==c['new'])).select(db.bot_context.context_json).first()
            import json
            caddena=str(newjson['context_json'])
            for s in cnt:
                caddena=caddena.replace(str(s['old']), str(s['new']))
            db((db.bot_context.bot_id==newBotId)&(db.bot_context.id==c['new'])).update(context_json=eval(caddena))
        return dict(cont=(r),cn=contexts,inte=intents,act=cnt,newbot=newBotId,status=respss)
        #return dict(cont=token)
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


@cors_allow
@request.restful()
def bot_variables_list():

    def GET(bot_id):
        variables = set()
        for variable in db(db.bot_storage.bot_id == bot_id).select():
            variables.add(variable.storage_key)

        return response.json(variables)

    return locals()

@cors_allow
@request.restful()
def variables():

    @decora('Segments')
    def GET(token):
        try:
            variables = set()
            for variable in db(db.bot_storage).select():
                variables.add(variable.storage_key)

            return response.json({'status': 'selected', 'data': variables})
        except:
            return response.json({'status': 'error', 'data': 'not founded variables'})

    return locals()

@cors_allow
@request.restful()
def broadcast():
    @decora('Segments')
    def GET(token, broadcast_id):
        if broadcast_id:
            broadcast = db(db.broadcasts.id == broadcast_id).select()
            if broadcast:
                return response.json(dict(status = 'founded', data = broadcast.first()))

            return response.json({'error': 'Broadcast with id {} not exists'.format(broadcast_id)})

    @decora('Segments')
    def POST(token, **vars):

        try:
            response_value = db.broadcast_rules_group.insert(**{'name': request.post_vars['name'], 'bot_id': request.post_vars['bot_id']})
            if response_value:
                created_broadcast = db(db.broadcast_rules_group.id == response_value).select().first()
                created_scheduler = scheduler.queue_task('send_broadcast', [created_broadcast.id])
                created_broadcast.update_record(scheduler_task_id = created_scheduler.result.id)
                return response.json({'status': 'created', 'data': created_broadcast})
            else:
                return response.json({'status': 'error', 'error': 'not created'})
        except:
            return response.json({'status': 'error', 'error': 'not created'})

    @decora('Segments')
    def PUT(token, **vars):

        try:
            response_evaluator = db(
                db.broadcast_rules_group.id==int(vars['id']),
            ).update(
                **vars
            )
            if response_evaluator:
                response_value = db(db.broadcast_rules_group.id == vars['id']).select().first()
                return response.json({'status': 'updated', 'data': response_value})
            else:
                return response.json({'status': 'error', 'error': 'not updated'})
        except:
            return response.json({'status': 'error', 'error': 'not updated'})

    @decora('Segments')
    def DELETE(token, **vars):

        response_evaluator = db(
            db.broadcast_rules_group.id==int(vars['id']),
        ).delete()

        if response_evaluator:
            return response.json({'status': 'deleted', 'data': vars})
        else:
            return response.json({'status': 'error', 'error': 'not deleted'})

    return locals()

@cors_allow
@request.restful()
def segments():

    @decora('Segments')
    def GET(token, **vars):

        segments = db(db.segments).select()
        return response.json({'status': 'selected', 'data': segments})

    return locals()

@cors_allow
@request.restful()
def broadcasts():

    @decora('Segments')
    def GET(token):
        broadcasts = db(db.broadcasts).select()
        return response.json({'status': 'selected', 'data': broadcasts})

    @decora('Segments')
    def POST(token, **vars):

        try:
            import datetime
            date_to_save = datetime.datetime.now()
            vars['created_at'] = date_to_save
            vars['updated_at'] = date_to_save
            vars['name'] = 'broadcast-' + str(date_to_save)
            vars['info'] = [
                {
                    'label': 'broadcast with name {} was created'.format(vars['name']),
                    'date': date_to_save,
                    'message': ""
                }
            ]
            response_value = db.broadcasts.insert(**vars)
            if response_value:
                created_broadcast = db(db.broadcasts.id == response_value).select().first()
                created_task = scheduler.queue_task('send_broadcast', [created_broadcast.id, "ALL"])
                created_broadcast.update_record(scheduler_task = created_task.id)
                return response.json({'status': 'created', 'data': created_broadcast})
            else:
                return response.json({'status': 'error', 'error': 'not created'})
        except:
            return response.json({'status': 'error', 'error': 'not created'})

    @decora('Segments')
    def PUT(token, **vars):
        import datetime
        date_to_save = datetime.datetime.now()
        params = dict(id = vars['id'], recurrent_users = vars['recurrent_users'], recurrent_time = vars['recurrent_time'], updated_at = date_to_save)
        broadcast = db(db.broadcasts.id == vars['id']).select().first()
        broadcast.update_record(**params)
        return response.json(dict(status = 'updated', data = broadcast))

    return locals()

#bots custom service
@cors_allow
@request.restful()
def bots():
    @decora('Segments')
    def GET(token, **vars):

        if(vars['segment_id']):
            segments = db(db.segments.id == vars['segment_id']).select()
            if segments:
                segment = segments.first()
                comparation = segment.comparation
                variables = set()
                bots = []
                bots_ids = set()
                #get segment variables name
                for filter in segment.filters:
                    variables.add(filter['variable'])

                for variable in variables:
                    for bot in db(db.bot_storage.storage_key == variable).select(db.bot_storage.bot_id):
                        bots_ids.add(bot.bot_id)
                #get bot info with bots ids
                try:
                    if int(vars['bot_id']):
                        bots_ids = [int(vars['bot_id'])]
                        for bot in bots_ids:
                            bot_to_insert = db(db.bot.id == bot).select(db.bot.id, db.bot.name).first()
                            bots.append(bot_to_insert)
                    else:
                        for bot in bots_ids:
                            bot_to_insert = db(db.bot.id == bot.id).select(db.bot.id, db.bot.name).first()
                            bots.append(bot_to_insert)
                except:
                    for bot in bots_ids:
                        bot_to_insert = db(db.bot.id == bot.id).select(db.bot.id, db.bot.name).first()
                        bots.append(bot_to_insert)
                #bot operations
                for bot in bots:
                    bot.variables = []
                    #get bot individual variables
                    for register in db(db.bot_storage.bot_id == bot.id).select():
                        if register.storage_key in variables:
                            bot.variables.append(register.storage_key)
                    #set bot variables to use
                    bot.variables = list(set(bot.variables))

                fake_bots = []

                if segment.comparation == 'AND':
                    for bot in bots:
                        if len(bot.variables) == len(variables):
                            fake_bots.append(bot)

                    bots = fake_bots

                for bot in bots:
                    bot.users = []
                    bot.qualified_users = []
                    users_ids = []
                    users_pivot = []
                    #get bot individual variables

                    for register in db(db.bot_storage.bot_id == bot.id).select():
                        if register.storage_key in variables:
                            users_ids.append(register.storage_owner)

                    #set bot user id to use
                    users_ids = list(set(users_ids))
                    #change to user object
                    for user in users_ids:
                        user = {'id': user}
                        users_pivot.append(user)
                    #user objects need data
                    for user in users_pivot:
                        responses = []
                        #get response with segment variables
                        for resp in db(
                            (db.bot_storage.bot_id == bot.id) &
                            (db.bot_storage.storage_owner == user['id'])
                        ).select(db.bot_storage.storage_key, db.bot_storage.storage_value):
                            if resp.storage_key in variables:
                                if segment.comparation == 'AND':
                                    resp['status'] = True
                                elif segment.comparation == 'OR':
                                    resp['status'] = False
                                responses.append(resp)
                        user['responses'] = responses
                        user['qualified'] = None
                    bot.users = users_pivot

                for bot in bots:
                    for user in bot.users:
                        fake_user = user
                        fake_user['filters'] = []
                        if segment.comparation == 'AND':
                            use_filters = segment.filters
                        elif segment.comparation == 'OR':
                            use_filters = []
                            for filter in segment.filters:
                                if filter['variable'] in bot['variables']:
                                    use_filters.append(filter)
                        for filter in use_filters:
                            user_response = next(item for item in user['responses'] if item['storage_key'] == filter['variable'])
                            comparation = {'filter_value': None, 'user_value': None, 'filter_comparation': filter['comparation'], 'status': False}

                            if filter['type'] == 'date':
                                from datetime import datetime
                                comparation['user_value'] = datetime.strptime(user_response['storage_value'],  "%d/%m/%Y")
                                comparation['filter_value'] = datetime.strptime(filter['value'],  "%Y-%m-%d")
                            elif filter['type'] == 'numeric':
                                comparation['user_value'] = int(user_response['storage_value'])
                                comparation['filter_value'] = int(filter['value'])
                            else:
                                comparation['user_value'] = user_response['storage_value']
                                comparation['filter_value'] = filter['value']

                            if filter['comparation'] == 'equals':
                                if comparation['user_value'] == comparation['filter_value']:
                                    comparation['status'] = True
                            if filter['comparation'] == 'not-equals':
                                if comparation['user_value'] != comparation['filter_value']:
                                    comparation['status'] = True

                            if (filter['comparation'] == 'greater-than') | (filter['comparation'] == 'after'):
                                if comparation['user_value'] > comparation['filter_value']:
                                    comparation['status'] = True
                            if (filter['comparation'] == 'smaller-than') | (filter['comparation'] == 'before'):
                                if comparation['user_value'] < comparation['filter_value']:
                                    comparation['status'] = True

                            if segment.comparation == 'AND':
                                if not comparation['status']:
                                    response_index = user['responses'].index(user_response)
                                    user['responses'][response_index]['status'] = False

                            elif segment.comparation == 'OR':
                                if comparation['status']:
                                    response_index = user['responses'].index(user_response)
                                    user['responses'][response_index]['status'] = True

                            fake_user['filters'].append(comparation)

                    if segment.comparation == 'OR':
                        for user in bot.users:
                            user['qualified'] = False
                            limit = len(user['responses']) - 1
                            position = 0
                            while True:
                                result = user['responses'][position]['status']
                                position = position + 1
                                if(result):
                                    user['qualified'] = True
                                    break
                                if position > limit:
                                    break

                            if user['qualified']:
                                bot.qualified_users.append(user)

                    if segment.comparation == 'AND':
                        for user in bot.users:
                            user['qualified'] = True
                            limit = len(user['responses']) - 1
                            position = 0
                            while True:
                                result = user['responses'][position]['status']
                                position = position + 1
                                if not result:
                                    user['qualified'] = False
                                    break
                                if position > limit:
                                    break

                            if user['qualified']:
                                bot.qualified_users.append(user)

                    try:
                        if vars['show_users']:
                            bot['users_count'] = len(bot['users'])
                            bot['qualified_users_count'] = len(bot['qualified_users'])
                            if(vars['show_users'] != 'true'):
                                del bot['users']
                                del bot['qualified_users']
                            else:
                                del bot['users']
                    except:
                        bot['users_count'] = len(bot['users'])
                        bot['qualified_users_count'] = len(bot['qualified_users'])
                        del bot['users']
                        del bot['qualified_users']

                return response.json({'status': 'founded', 'data': bots})
            else:
                return response.json({'status': 'error', 'error': 'not founded'})

    return locals()

@cors_allow
@request.restful()
def segment():

    @decora('Segments')
    def GET(token, segment_id):
        segment = db(db.segments.id == segment_id).select()
        if segment:
            return response.json({'status': 'selected', 'data': segment.first()})

        return response.json({'status': 'error', 'error': 'not founded'})

    @decora('Segments')
    def POST(token, **vars):

        try:
            import datetime
            date_to_save = datetime.datetime.now()
            vars['created_at'] = date_to_save
            vars['updated_at'] = date_to_save
            response_value = db.segments.insert(**vars)
            if response_value:
                created_segment = db(db.segments.id == response_value).select().first()
                return response.json({'status': 'created', 'data': created_segment})
            else:
                return response.json({'status': 'error', 'error': 'not created'})
        except:
            return response.json({'status': 'error', 'error': 'not created'})

    @decora('Segments')
    def PUT(token, **vars):

        try:
            import datetime
            vars['updated_at'] = datetime.datetime.now()
            response_evaluator = db(
                db.segments.id==int(vars['id']),
            ).update(
                **vars
            )
            if response_evaluator:
                response_value = db(db.segments.id == vars['id']).select().first()
                return response.json({'status': 'updated', 'data': response_value})
            else:
                return response.json({'status': 'error', 'error': 'not updated'})
        except:
            return response.json({'status': 'error', 'error': 'not updated'})

    @decora('Segments')
    def DELETE(token, **vars):

        response_evaluator = db(
            db.segments.id==int(vars['id']),
        ).delete()

        if response_evaluator:
            return response.json({'status': 'deleted', 'data': vars})
        else:
            return response.json({'status': 'error', 'error': 'not deleted'})

    return locals()

@cors_allow
@request.restful()
def send_broadcast():

    @decora('Segments')
    def POST(token,**vars):
        broadcast_id = vars['broadcast_id']
        broadcast = db(db.broadcasts.id == broadcast_id).select().first()
        broadcast.update_record(status='working')
        send_type = vars['send_type']
        result = scheduler.queue_task('send_broadcast', [broadcast_id, send_type])
        return response.json(dict(result = result))

    return locals()

@cors_allow
@request.restful()
def create_recurrent_broadcast():

    @decora('Segments')
    def POST(token, **vars):
        import datetime
        import json
        date_to_update = datetime.datetime.now()
        broadcast_id = vars['broadcast_id']
        task_activate = vars['task_activate']
        broadcast = db(db.broadcasts.id == broadcast_id).select().first()
        task = db(db.scheduler_task.id == broadcast.scheduler_task).select().first()
        args = [broadcast.id, broadcast.recurrent_users]
        if task_activate == 'true':
            broadcast.update_record(recurrent_active = True, updated_at = date_to_update)
            task.update_record(args = json.dumps(args), repeats = 0, period = int(broadcast.recurrent_time), status='QUEUED')
        else:
            broadcast.update_record(recurrent_active = False, updated_at = date_to_update)
            task.update_record(repeats = 1, status='COMPLETED')
        return response.json(dict(status = 'updated', data = broadcast, task = task))

    return locals()

@cors_allow
@request.restful()
def contexts():
    @decora('Segments')
    def GET(token, **vars):
        bot_id = None
        try:
            bot_id = vars['bot_id']
        except:
            return response.json(dict(status = 'error', error = 'not id specified'))

        if bot_id:
            bots = db(db.bot.id == bot_id).select()
            if len(bots) > 0:
                bot = bots.first()
                contexts = db(db.bot_context.bot_id == bot_id).select(db.bot_context.id, db.bot_context.name)
                return response.json(dict(status = 'selected', data = contexts))
            else:
                return response.json(dict(status = 'error', error = 'bot with id not exists'))

    return locals()
#---------------------------------------------------------------------
@cors_allow
@request.restful()
def location_webview_user():
    response.view = 'generic.' + request.extension
    def POST(psid,depto,muni,bot_id):
        deptos=db.bot_storage.update_or_insert((db.bot_storage.storage_owner == psid)&
                                                    (db.bot_storage.bot_id == bot_id)&
                                                    (db.bot_storage.storage_key =='departamento'),
                                                  storage_owner = psid,
                                                  bot_id = bot_id,
                                                  storage_key='departamento',
                                                  storage_value=depto)
        munis=db.bot_storage.update_or_insert((db.bot_storage.storage_owner == psid)&
                                                    (db.bot_storage.bot_id == bot_id)&
                                                    (db.bot_storage.storage_key =='municipio'),
                                                  storage_owner = psid,
                                                  bot_id = bot_id,
                                                  storage_key='municipio',
                                                  storage_value=muni)
        #-------------------------------------------------------------------------------------------------------------
        import requests
        status = []
        uri = 'https://demo-backend.botprotec.com/backend/webhook/hook/messenger/%s.json' % (bot_id)
        print('result in user {user}'.format(user = psid))
        status.append(dict(user_id = psid))
        request_body = dict(
            entry = [
                dict(
                    messaging = [
                        dict(
                            message = dict(text = 'siguiente bloque'),
                            sender = dict(id = psid)
                        )
                    ]
                )
            ]
        )
        print(request_body)
        resu = requests.post(uri, json=request_body)
        print(resu.json())
        #-------------------------------------------------------------------------------------------------------------
        return dict(deptos=deptos,munis=munis,psid=psid,bot=bot_id)
    return locals()
#---------------------------------------------------------------------
@cors_allow
@request.restful()
def calendar_webview():
    response.view = 'generic.' + request.extension
    def POST(psid,hora,fecha,bot_id):
        horita=db.bot_storage.update_or_insert((db.bot_storage.storage_owner == psid)&
                                                    (db.bot_storage.bot_id == bot_id)&
                                                    (db.bot_storage.storage_key =='meeting_time'),
                                                  storage_owner = psid,
                                                  bot_id = bot_id,
                                                  storage_key='meeting_time',
                                                  storage_value=hora)
        fechita=db.bot_storage.update_or_insert((db.bot_storage.storage_owner == psid)&
                                                    (db.bot_storage.bot_id == bot_id)&
                                                    (db.bot_storage.storage_key =='meeting_date'),
                                                  storage_owner = psid,
                                                  bot_id = bot_id,
                                                  storage_key='meeting_date',
                                                  storage_value=fecha)
        #-------------------------------------------------------------------------------------------------------------
        import requests
        status = []
        #--------bantrab--------------
        #uri = 'https://des-backend-chatbot.bantrab.com.gt/backend/webhook/hook/messenger/%s.json' % (bot_id)
        #----------------ambiente demo-------------------------------
        uri = 'https://demo-backend.botprotec.com/backend/webhook/hook/messenger/%s.json' % (bot_id)
        print('result in user {user}'.format(user = psid))
        status.append(dict(user_id = psid))
        request_body = dict(
            entry = [
                dict(
                    messaging = [
                        dict(
                            message = dict(text = 'siguiente bloque'),
                            sender = dict(id = psid)
                        )
                    ]
                )
            ]
        )
        print(request_body)
        #bantrab--------------------
        #resu = requests.post(uri, json=request_body,verify=False)
        resu = requests.post(uri, json=request_body)
        print(resu.json())
        return dict(hora=horita,fecha=fechita)
    return locals()
#--------------------------------------------------------------------------------------
@cors_allow
@request.restful()
def auth_log():
    response.view = 'generic.' + request.extension
    @decora('User Manager')
    def GET(token):#es POST
        maxID=db(db.history_user).select(db.history_user.id.max()).first()[db.history_user.id.max()]
        ids=int(str(maxID))-30
        seleccion=db(db.history_user.id>=ids).select(orderby=~db.history_user.id)
        #seleccion=db(db.history_user.id>0).select()
        return dict(data = seleccion)
    return locals()
@cors_allow
@request.restful()
def history_rows():
    response.view = 'generic.' + request.extension
    @decora('User Manager')
    def GET(token,filas):#es POST
        maxID=db(db.history_user).select(db.history_user.id.max()).first()[db.history_user.id.max()]
        ids=int(str(maxID))-int(filas)
        seleccion=db(db.history_user.id>=ids).select(orderby=~db.history_user.id)
        return dict(data = seleccion)
    return locals()
#-----------------------------------------------------------------------------------
@cors_allow
@request.restful()
def values_users():
    response.view = 'generic.' + request.extension
    #@decora('Bot Chat Center')
    def POST(token,id,owner):
        resultado=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_value<>None)&(db.bot_storage.storage_key<>None)&
                  (db.bot_storage.storage_value<>"")&(db.bot_storage.storage_key<>"") &(db.bot_storage.storage_owner==owner)).select(
                  db.bot_storage.storage_key,db.bot_storage.storage_value,distinct=True)
        return dict(content =resultado)
    return locals()
@cors_allow
@request.restful()
def delete_variable():
    response.view = 'generic.' + request.extension
    #@decora('Bot Chat Center')
    def POST(token,id,owner,key,value):
        borrar=db((db.bot_storage.bot_id==id)&(db.bot_storage.storage_owner==owner)&
           (db.bot_storage.storage_key==key)&(db.bot_storage.storage_value==value)).delete()
        return dict(data =borrar)
    return locals()
@cors_allow
@request.restful()
def insert_variable():
    response.view = 'generic.' + request.extension
    #@decora('Bot Chat Center')
    def POST(token,id,owner,key,value):
        seleccion=db.bot_storage.insert(bot_id=id,storage_owner=owner,storage_key=key,storage_value=value)
        return dict(data =seleccion)
    return locals()