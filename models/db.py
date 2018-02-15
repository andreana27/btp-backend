# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
auth.settings.extra_fields['auth_user']= [
  Field('api_token', 'string'),
  Field('token_datetime', 'datetime')]
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('contact',
               Field('firstName', 'string'),
               Field('lastName', 'string'),
               Field('email', 'string'),
               Field('phoneNumber', 'string'))
import os
db.define_table('bot',
                Field('name','string'),
                Field('enabled','boolean',default=True ),
                Field('bot_language','string',default='en' ),
                Field('picture','upload', default = os.path.join(request.folder, 'static', 'images', 'bot_avatar.png')),
                Field('connectors', 'json'))
#bot default image
#import os
#db.bot.picture.default = os.path.join(request.folder, 'static', 'images', 'bot-avatar.png')


db.define_table('bot_storage',
                Field('bot_id', 'reference bot'),
                Field('storage_owner', 'string'),
                Field('storage_key', 'string'),
                Field('storage_value', 'string'))

db.define_table('bot_internal_storage',
                Field('bot_id', 'reference bot'),
                Field('storage_owner', 'string'),
                Field('storage_key', 'string'),
                Field('storage_value', 'string'))

db.define_table('bot_context',
                Field('bot_id', 'reference bot'),
                Field('parent_context', 'reference bot_context'),
                Field('isdefault', 'boolean', default = False),
                Field('name', 'string'),
                Field('context_json', 'json'))

db.define_table('conversation',
                Field('bot_id', 'reference bot'),
                Field('storage_owner', 'string'),
                Field('ctype', 'string'),
                Field('ccontent', 'text'),
                Field('message_date', 'date'),
                Field('message_time', 'time'),
                Field('origin', 'string'),
                Field('medium', 'string'),
               Field('content_type', 'string'))

db.define_table('website_token',
                Field('bot_id', 'reference bot'),
                Field('website', 'string'),
                Field('token', 'string'))

db.define_table('bot_intent',
                Field('bot_id', 'reference bot'),
                Field('context_id', 'reference bot_context'),
                Field('name', 'string'))

db.define_table('intent_context_example',
                Field('intent_id', 'reference bot_intent'),
                Field('example_text', 'string'))

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
