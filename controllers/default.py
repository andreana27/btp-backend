# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
def preCalificador():
    xml = request.body.read()  # retrieve the raw POST data
    return dict(message="hello from apiRest.py")

import json
def preCalificador():
    #with open("json.txt","a") as f:
    #    json.dump(request.vars,f)
    dataB = request.body.read()
    myfile = os.path.join('/home/rasa/rasa_nlu/data/examples/rasa/', 'result.json')
    f = open(myfile,'w')
    arrData = dataB.split("&")
    for d in arrData:
        params = d.split("=")
        if(str(params[0])=='DPI'):
            try:
                num = long(str(params[1]))
                if num%2 == 0:
                    return str("Tu crédito ha sido pre-aprobado! Uno de nuestros agentes te contactará en las siguientes horas. Ten listo tu DPI y un recibo de algún servicio.")
                else:
                    return str("Lastimosamente tu crédito no ha sido pre-aprobado.")
            except ValueError:
                return str("No se pudo evaluar el código ingresado.")
        f.write(str(params[0]))
    f.close()
    return str(dataB)

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

@cors_allow
def user():
    response.view = 'generic.' + request.extension
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def csvExport():
    scriptId = 1
	#rows = db(query,ignore_common_filters=True).select()
    rows2 = db(db.bot_storage.bot_id == 11).select(db.bot_storage.storage_owner,distinct=True)
    rows = db(db.bot_storage.bot_id == 11).select(db.bot_storage.storage_key, db.bot_storage.storage_owner, db.bot_storage.storage_value, limitby=(0,2000))
    from gluon.contenttype import contenttype
    response.headers['Content-Type'] = contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=export_%s.csv' % (scriptId)
    import csv, cStringIO
    s = cStringIO.StringIO()
    myList2=[]
    data = db(db.bot_storage.bot_id == 11).select(db.bot_storage.storage_key, distinct=True)
    myList=[]
    for value in data:
        myList.append(value.storage_key)
    myList2.append(myList)
    for rowowner in rows2:
        myList=[]
        for value in data:
            dato = db((db.bot_storage.bot_id == 11) & (db.bot_storage.storage_owner == rowowner.storage_owner) & (db.bot_storage.storage_key == value.storage_key)).select(db.bot_storage.storage_value).first()
            if dato != None:
                myList.append(dato.storage_value)
            else:
                myList.append(" ")
        myList2.append(myList)
    import numpy as np
    myarray = np.array(myList2)
    rows2.export_to_csv_file(s, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    import csv

    myFile = open('/opt/web2py_apps/web2py.production/applications/backend/static/example4.csv', 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(myList2)

    print("Writing complete")
    return s.getvalue()
