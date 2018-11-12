# -*- coding: utf-8 -*-

def cors_origin():
    allowed_origins = {'http://au.innovare.es':'http://au.innovare.es',
                       'http://a1.botprotec.com':'http://a1.botprotec.com',
                       'https://demo.botprotec.com':'https://demo.botprotec.com',
                       'https://bancredit.botprotec.com':'https://bancredit.botprotec.com',
                       'https://grupo-veraz.botprotec.com':'https://grupo-veraz.botprotec.com',
                       'http://localhost:9090': 'http://localhost:9090',
                       'http://localhost:9000': 'http://localhost:9000'}
    o = "%s" %(request.env['HTTP_ORIGIN'])
    origin = allowed_origins.get(o)
    headers = {}
    headers['Access-Control-Allow-Origin'] = origin

    headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, POST, HEAD, PUT, DELETE'
    headers['Access-Control-Allow-Headers'] = 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,Accept'
    headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers.update(headers)

    if request.env.request_method == 'OPTIONS':
        headers['Content-Type'] = None
        raise HTTP(200, '', **headers)


def cors_allow(action):

    def f(*args, **kwargs):
        cors_origin()
        return action(*args, **kwargs)

    f.__doc__ = action.__doc__
    f.__name__ = action.__name__
    f.__dict__.update(action.__dict__)

    return f
#---------------------------------------------------
