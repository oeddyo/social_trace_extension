from flask import Flask
from flask import jsonify


from app import app

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from flask import make_response
from functools import update_wrapper

import random
import uuid
import mongo


import inspect
import os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import predict_gender.genderPredictor as GP

import gdata.youtube.service
import json

yts = gdata.youtube.service.YouTubeService()
gp = GP.genderPredictor()
gp.trainAndTest()

record_db = mongo.connect('record')
page_db = mongo.connect('page')
survey_db = mongo.connect('survey')


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


def get_id_from_uri(uri):
    pos1 = uri.find("v=")
    pos2 = uri[pos1+1:len(uri)].find("&")
    if pos2!=-1:
        pos2 = pos2 + pos1 + 1
        pos2 = min(pos2, len(uri))
    else:
        pos2 = len(uri)
    pos1 += 2  
    video_id = uri[pos1: pos2]
    return video_id

def count_gender_on_page(uri):  
    video_id = get_id_from_uri(uri)
    print "#"+video_id+"#"
    ytfeed = yts.GetYouTubeVideoCommentFeed(video_id=video_id)
    names = [name.author[0].name.text  for name in ytfeed.entry]
    male = 0
    female = 0
    for name in names:
        classfied_result = gp.classify(name)
        if classfied_result == 'M':
            male += 1
        elif classfied_result == 'F':
            female += 1
        else:
            continue
    return male, female 
   

def randomly_assign_condition():
    condition_list = ['gender', 'location', 'empty']

    first_category = random.randint(0, len(condition_list)-1)
    print "random number = ", first_category
    if first_category == 0:
        second_category = random.randint(0, 2)  # add/normal/subtract
        if second_category == 0:
            return condition_list[0] + "_" + "more"
        elif second_category == 1:
            return condition_list[0] + "_" + "normal"
        else:
            return condition_list[0] + "_" + "less"
    else:
        return condition_list[first_category]


@app.route('/store_survey', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def store_survey():
    from pprint import pprint

    if request.method == 'POST':
        print dir(request)
        print request.form
        print request.form.getlist('email')
        print dir(request.form)
        print request.form.to_dict()
        condition = randomly_assign_condition()
        d = request.form.to_dict()
        d['condition'] = condition
        survey_db.insert(d)
        return "ok"
    return "ok"

# need to store into mongo
def get_geo():
    return int(random.random()*100)

@app.route('/get_page_config', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def get_page_config():
    if request.method == 'POST':
        "see if the page is in db already"
        uri = json.loads(request.data)['uri']
        user_id = json.loads(request.data)['user_id']

        user_info = [s for s in survey_db.find({'user_id': user_id})]

        if user_id == None or len(user_info) == 0:
            print 'retuning survey needed...'
            return jsonify({'response': 2})
        else:
            user_info = user_info[0]

        user_gender = user_info['gender']
        user_condition = user_info['condition']
        page_id = get_id_from_uri(uri)
        info = {}

        query = {"_id": {'page_id': page_id, 'user_id': user_id}}
        if page_db.find(query).count() == 0:
            # insert here
            male, female = count_gender_on_page(uri)
            scale = 0.0

            if user_gender == 'Male':
                scale = male*1.0/(male+female)
            else:
                scale = female*1.0/(male+female)

            info['gender'] = {'same_gender_scale':scale }
            #info['gender'] = {'male':male, 'female': female} 
            info['geo'] = get_geo()
            info['_id'] = {'page_id': page_id, 'user_id': user_id}
            page_db.insert(info)
        else:
            info = [p for p in page_db.find(query)][0]
            print 'retrival ', info
        return jsonify(info)


# response
# 0: successful
# 1: fail
# 2: need survey

@app.route('/store', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def store():
    if request.method == 'POST':
        print request.data
        print type(request.data)
        print 'ready to insert'
        
        try:
            record_db.insert(json.loads(request.data))
        except:
            print 'error inserting...'
        return jsonify(
                {"response": 0}
        )

    else:
        print 'here'
    return jsonify({"response":1})




@app.route('/get_id_from_server')
@crossdomain(origin='*')
def assign_id():
    _id = uuid.uuid4()
    print str(_id)
    return str(_id)

