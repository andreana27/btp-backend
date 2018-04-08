# -*- coding: utf-8 -*-
# intente algo como
def preCalificador():
    xml = request.body.read()  # retrieve the raw POST data
    return dict(message="hello from apiRest.py")

def index(): return dict(message="hello from apiRest.py")
