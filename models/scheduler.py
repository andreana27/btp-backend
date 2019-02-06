# -*- coding: utf-8 -*-
import time
from datetime import datetime

def get_users(segment_id, bot_id):
    segments = db(db.segments.id == segment_id).select()
    bots = db(db.bot.id == bot_id).select()
    if segments and bots:
        segment = segments.first()
        bot = bots.first()
        filters = segment['filters']
        apply_filters = []
        qualified_users = []

        #get users id
        users_id = set()
        variables = set()
        bot_variables = set()
        for register in db(db.bot_storage.bot_id == bot.id).select():
            users_id.add(register.storage_owner)

        #get segment variables
        for filter in filters:
            variables.add(str(filter['variable']))

        #get bot variables
        for register in db(db.bot_storage.bot_id == bot.id).select():
            if register.storage_key in variables:
                bot_variables.add(register.storage_key)

        #get users
        users = []
        for user_id in users_id:
            user = {"id": user_id, "responses": [], "comparations": [], "qualified": False}
            users.append(user)

        #get responses for user
        for user in users:
            for register in db(db.bot_storage.storage_owner == int(user['id'])).select(db.bot_storage.storage_key, db.bot_storage.storage_value):
                if register.storage_key in variables:
                    if segment.comparation == 'AND':
                        register['status'] = True
                    elif segment.comparation == 'OR':
                        register['status'] = False
                    user['responses'].append(register)

        #get apply filters
        for filter in filters:
            if filter['variable'] in bot_variables:
                apply_filters.append(filter)

        #check user response with filters
        for user in users:
            #list filters to compare
            for filter in apply_filters:
                #get user response with variable in filter
                try:
                    user_response = next(item for item in user['responses'] if item['storage_key'] == filter['variable'])
                except:
                    pass
                #create comparation dict for check values
                comparation = {'filter_value': None, 'user_value': None, 'filter_comparation': filter['comparation'], 'status': False}

                #filter variable type based
                if filter['type'] == 'date':
                    comparation['user_value'] = datetime.strptime(user_response['storage_value'],  "%d/%m/%Y")
                    comparation['filter_value'] = datetime.strptime(filter['value'],  "%Y-%m-%d")
                elif filter['type'] == 'numeric':
                    comparation['user_value'] = int(user_response['storage_value'])
                    comparation['filter_value'] = int(filter['value'])
                else:
                    comparation['user_value'] = user_response['storage_value']
                    comparation['filter_value'] = filter['value']

                #compare value with filter
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

                #check if comparation is not valid, if not valid, response status false
                if segment.comparation == 'AND':
                    if not comparation['status']:
                        try:
                            response_index = user['responses'].index(user_response)
                            user['responses'][response_index]['status'] = False
                        except:
                            pass

                #check if comparation is valid, if valid, response status true
                elif segment.comparation == 'OR':
                    if comparation['status']:
                        try:
                            response_index = user['responses'].index(user_response)
                            user['responses'][response_index]['status'] = True
                        except:
                            pass

                user['comparations'].append(comparation)

        if segment.comparation == 'OR':
            for user in users:
                user['qualified'] = False
                limit = len(user['responses']) - 1
                position = 0
                while True:
                    try:
                        result = user['responses'][position]['status']
                        position = position + 1
                    except:
                        pass
                    if(result):
                        user['qualified'] = True
                        break
                    if position > limit:
                        break
            print('users OR: {}'.format(users))

        if segment.comparation == 'AND':
            for user in users:
                user['qualified'] = True
                limit = len(user['responses']) - 1
                position = 0
                while True:
                    try:
                        result = user['responses'][position]['status']
                        position = position + 1
                    except:
                        pass
                    if not result:
                        user['qualified'] = False
                        break
                    if position > limit:
                        break
            print('users AND: {}'.format(users))

        print('segment comparation is: {}'.format(segment.comparation))
        '''print('bot name is: {}'.format(bot.name))
        print('variables: {}'.format(variables))
        print('bot variables: {}'.format(bot_variables))
        print('apply filters: {}'.format(apply_filters))'''
        for user in users:
            if user['qualified']:
                qualified_users.append(user['id'])
        return qualified_users
    else:
        print('error')
        return []

def send_message_to_telegram():
    print('telegram here! O/')
    return True

def send_message_to_messenger(bot_token, users, message, broadcast):
    import requests
    affected_users = 0
    results = []
    uri = 'https://graph.facebook.com/v2.6/me/messages?access_token={token}'.format(token = bot_token)
    print("uri: " + uri)
    for user in users:
        broadcast_body = dict(recipient = dict(id = user),message = dict(text = message))
        resu = requests.post(uri, json=broadcast_body)
        results.append(resu.json())
        affected_users = affected_users + 1
        broadcast.update_record(affected_users = int(affected_users))
        db.commit()
    return results

def send_message(bot_id, users, message, broadcast):
    bot = db(db.bot.id == bot_id).select().first()
    result = None
    if bot:
        connectors = bot['connectors']
        for connector in connectors:
            if connector['type'] == 'messenger':
                result = send_message_to_messenger(connector['token'], users, message, broadcast)
            elif connector['type'] == 'telegram':
                send_message_to_telegram()
        return result
    else:
        return False

def change_context(bot_id, users, context_id, broadcast):
    import requests
    status = []
    affected_users = 0
    uri = '%s://%s%s' % (request.env.wsgi_url_scheme, request.env.http_host,
               request.env.web2py_original_uri)
    #---------bancredit-------------------------------------------------
    #uri = 'https://backend-bancredit.botprotec.com/backend/webhook/hook/messenger/%s.json' % (bot_id)
    #--------------------ambiente demo-----------------------------------------
    uri = 'https://demo-backend.botprotec.com/backend/webhook/hook/messenger/%s.json' % (bot_id)
    #----bantrab----------------------------------
    #uri = 'https://des-backend-chatbot.bantrab.com.gt/backend/webhook/hook/messenger/%s.json' % (bot_id)
    for user in users:
        print('bot id: {} user id: {} context id: {}'.format(bot_id, user, context_id))
        result =  db.bot_internal_storage.update_or_insert(
            (db.bot_internal_storage.storage_owner == user) &
            (db.bot_internal_storage.bot_id == bot_id) &
            (db.bot_internal_storage.storage_key == 'current_context'),
            storage_owner = user,
            bot_id = bot_id,
            storage_key = 'current_context',
            storage_value = int(context_id)
        )
        db.bot_internal_storage.update_or_insert(
            (db.bot_internal_storage.storage_owner == user) &
            (db.bot_internal_storage.bot_id == bot_id) &
            (db.bot_internal_storage.storage_key == 'flow_position'),
            storage_owner = user,
            bot_id = bot_id,
            storage_key = 'flow_position',
            storage_value = 0
        )
        affected_users = affected_users + 1
        broadcast.update_record(affected_users = int(affected_users))
        db.commit()
        print('result in user {user} is: {result}'.format(user = user, result = result))
        status.append(dict(user_id = user, result_query = result))
        request_body = dict(
            entry = [
                dict(
                    messaging = [
                        dict(
                            message = dict(text = 'changed to context'),
                            sender = dict(id = user)
                        )
                    ]
                )
            ]
        )
        print(request_body)
        resu = requests.post(uri, json=request_body)
        print(resu.json())
    return status

def send_broadcast(broadcast_id, send_type):
    broadcasts = db(db.broadcasts.id == broadcast_id).select()
    if broadcasts:
        broadcast = broadcasts.first()
        action = broadcast.action_type
        value = broadcast.action_value
        #get apply users
        users = get_users(broadcast.segments_id, broadcast.bot_id)
        #get last affected users
        last_affected_users = broadcast.affected_users_json['data']
        #save only broadcast users
        broadcast_users = []
        if send_type == 'NEW':
            for user in users:
                if user not in last_affected_users:
                    broadcast_users.append(user)
        elif send_type == 'ALL':
            broadcast_users = users
        print('broadcast users to send message')
        print(broadcast_users)
        #set working status
        date_now = datetime.now()
        info = broadcast.info
        info.append(dict(date = date_now, label = "broadcast {} has started.".format(broadcast.name),
                         message = "{} estimated users".format(len(broadcast_users))))
        broadcast.update_record(status = 'working', users = len(users), info = info, affected_users = 0)
        db.commit()
        #set action
        if action == 'send_message':
            operation_result = send_message(broadcast.bot_id, broadcast_users, value, broadcast)
        elif action == 'change_context':
            operation_result = change_context(broadcast.bot_id, broadcast_users, value, broadcast)
        time.sleep(5)
        #update history info
        info = broadcast.info
        date_updated = datetime.now()
        info.append(dict(
                date = date_updated,
                label = "broadcast {} has finished.".format(broadcast.name),
                message = "{} affected users".format(broadcast.affected_users)))
        broadcast.update_record(status='completed', info = info, affected_users_json = dict(data = users))
        db.commit()

        return dict(
            broadcast_id = broadcast.id,
            bot_id = broadcast.bot_id,
            segment_id = broadcast.segments_id,
            users = users,
            action = action,
            value = value,
            result = operation_result
        )
    else:
        print("not broadcast")
        return None

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)
