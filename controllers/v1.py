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
        result = db[table_name].validate_and_insert(**vars)
        return dict(content = db(db[table_name]._id == result.id).select(), errors = result.errors)
    def PUT(table_name,record_id,**vars):
        db(db[table_name]._id==record_id).update(**vars)
        return dict(content = db(db[table_name]._id == record_id).select())
    return locals()
