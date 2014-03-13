__author__ = 'eddiexie'
from app import app
import random

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
    ytfeed = app.yts.GetYouTubeVideoCommentFeed(video_id=video_id)
    names = [name.author[0].name.text  for name in ytfeed.entry]
    male = 0
    female = 0
    for name in names:
        classfied_result = app.gp.classify(name)
        if classfied_result == 'M':
            male += 1
        elif classfied_result == 'F':
            female += 1
        else:
            continue
    return male, female

def randomly_assign_condition():
    condition_list = ['gender', 'location', 'control']

    first_category = random.randint(0, len(condition_list)-1)
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

def get_geo():
    return int(random.random()*100)
