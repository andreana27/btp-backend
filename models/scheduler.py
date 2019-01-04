# -*- coding: utf-8 -*-
import time

def send_broadcast(segment_id, bot_id):
    segments = db(db.segments.id == segment_id).select()
    bots = db(db.bot.id == bot_id).select()
    if segments and bots:
        segment = segments.first()
        bot = bots.first()
        filters = segment['filters']

        #get users id
        users_id = set()
        variables = set()
        bot_variables = set()
        for register in db(db.bot_storage.bot_id == bot.id).select():
            users_id.add(register.storage_owner)

        #get segment variables
        for filter in filters:
            variables.add(str(filter['variable']))

        #get users
        users = []
        for user_id in users_id:
            users.append({'id': user_id, 'responses': []})

        #get responses for user
        for user in users:
            for response in db(db.bot_storage.storage_owner == user['id']):
                if response.storage_key in variables:
                    user['responses'].append(response)

        print('segment name is: {}'.format(segment.name))
        print('bot name is: {}'.format(bot.name))
        print('variables: {}'.format(variables))
        print('users: {}'.format(users) )
        return segment.id
    else:
        print('error')
        return segment_id

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)
