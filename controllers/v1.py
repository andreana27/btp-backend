# -*- coding: utf-8 -*-
# intente algo como
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
        result = db[table_name].validate_and_insert(**vars)
        patterns = 'auto'
        table_name = table_name.replace('_','-')
        parser = db.parse_as_rest(patterns, [table_name], vars)
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
        #return dict(content = db(db[table_name]._id == record_id).select())
    return locals()
