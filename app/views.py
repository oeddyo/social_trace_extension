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

import social_trace_extension.predict_gender.genderPredictor as GP
import gdata.youtube.service
import json

yts = gdata.youtube.service.YouTubeService()
gp = GP.genderPredictor()
gp.trainAndTest()


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

@app.route('/get_condition')
@crossdomain(origin='*')
@nocache
def condition():
    male_ratio = int(random.random() * 100)
    female_ratio = 100 - male_ratio
    return jsonify(
            {"response": [male_ratio, female_ratio]}
    )


    
def count_gender_on_page(uri):  
    pos1 = uri.find("v=")
    pos2 = uri[pos1+1:len(uri)].find("&")
    if pos2!=-1:
        pos2 = pos2 + pos1 + 1
        pos2 = min(pos2, len(uri))
    else:
        pos2 = len(uri)
    pos1 += 2  
    video_id = uri[pos1: pos2]
    print pos1, pos2 
    print uri, video_id
    print "#"+video_id+"#"
    ytfeed = yts.GetYouTubeVideoCommentFeed(video_id=video_id)
    names = [name.author[0].name.text  for name in ytfeed.entry]
    male = 0
    female = 0
    for name in names:
        if gp.classify(name) == 'M':
            male += 1
        else:
            female += 1
    return male, female 
    
@app.route('/get_gender', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def get_gender():
    if request.method == 'POST':
        uri = json.loads(request.data)['uri']
        male_ratio, female_ratio = count_gender_on_page(uri)
        return jsonify(
                {"response": [male_ratio, female_ratio]}
        )
    return jsonify({"response": [male_ratio, female_ratio]})


@app.route('/store', methods=['GET', 'POST'])
@crossdomain(origin='*')
@nocache
def store():
    if request.method == 'POST':
        print request.data
        return jsonify(
                {"response": 1}
        )
    return jsonify({"response":1})



@app.route('/get_geo', methods=['GET'])
@crossdomain(origin='*')
@nocache
def get_geo():
    obj_to_return = {"geo": int(random.random()*100)}
    return jsonify(obj_to_return)


@app.route('/get_id_from_server')
@crossdomain(origin='*')
def assign_id():
    _id = uuid.uuid4()
    print str(_id)
    return str(_id)

