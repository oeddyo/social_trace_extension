from flask import jsonify
from app import app
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

import random
import uuid
import mongo
import json

from lib import count_gender_on_page
from lib import get_id_from_uri
from lib import randomly_assign_condition
from lib import get_geo

def nocache(f):
    def new_func(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.cache_control.no_cache = True
        return resp
    return update_wrapper(new_func, f)

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/')
def hello_world():
    return 'Hello World!'




@app.route('/store_survey', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def store_survey():
    if request.method == 'POST':
        condition = randomly_assign_condition()
        d = request.form.to_dict()
        d['condition'] = condition
        survey_db = mongo.connect('survey')
        survey_db.insert(d)
        return json.dumps({"response": "OK"})
    return json.dumps({"response": "ERROR"})


@app.route('/get_page_config', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def get_page_config():
    if request.method == 'POST':
        "see if the page is in db already"

        uri = json.loads(request.data)['uri']
        user_id = json.loads(request.data)['user_id']

        survey_db = mongo.connect('survey')
        user_info = [s for s in survey_db.find({'user_id': user_id})]
        if len(user_info)<=0 or u'gender' not in user_info[0]:
            print 'Returning Need Survey'
            return json.dumps({'response': "Need Survey"})

        user_info = user_info[0]

        user_gender = user_info['gender']
        user_condition = user_info['condition']
        user_info['condition'] = user_condition
        page_id = get_id_from_uri(uri)
        info = {'condition': user_condition}

        page_db = mongo.connect('page')

        male, female = count_gender_on_page(uri)

        if user_gender == 'Male':
            scale = male*1.0/(male+female)
        else:
            scale = female*1.0/(male+female)

        print 'before', scale
        if user_condition == 'gender_less':
            scale -= 0.2
        elif user_condition == 'gender_more':
            scale += 0.2

        scale = min(scale, 1.0)
        scale = max(scale, 0.0)
        print 'after', scale

        query = {"_id": {'page_id': page_id, 'user_id': user_id}}
        if page_db.find(query).count() == 0:
            info['same_gender_scale'] = scale
            info['geo'] = get_geo()
            info['_id'] = {'page_id': page_id, 'user_id': user_id}
            page_db.insert(info)
        else:
            info = [p for p in page_db.find(query)][0]
        
        return jsonify(info)

@app.route('/store_record', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def store_record():
    if request.method == 'POST':
        record_db = mongo.connect('record')
        record_db.insert(json.loads(request.data))
        return json.dumps({'response': "OK"})
    return json.dumps({'response': "ERROR"})
