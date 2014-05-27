__author__ = 'eddiexie'
import numpy as np
from app import app
import random
import gdata


GENDER_MORE = "gender_new_more"
GENDER_LESS = "gender_new_less"
GENDER_NORMAL = "gender_new_normal"


def get_id_from_uri(uri):
    pos1 = uri.find("v=")
    pos2 = uri[pos1 + 1:len(uri)].find("&")
    if pos2 != -1:
        pos2 = pos2 + pos1 + 1
        pos2 = min(pos2, len(uri))
    else:
        pos2 = len(uri)
    pos1 += 2
    video_id = uri[pos1: pos2]
    return video_id


def get_video_info(url):
    video_id = get_id_from_uri(url)
    try:
        entry = app.yts.GetYouTubeVideoEntry(video_id=video_id)
        error_code = None
    except gdata.service.RequestError, inst:
        error_code = inst[0]

    video_info = {'title': None, 'published_on': None, 'description': None, 'category': None, 'tags': None,
                  'duration_seconds': None, 'geo': None,
                  'view_count': None, 'rating': None}
    if error_code is None:
        try:
            video_info['title'] = entry.media.title.text
            video_info['published_on'] = entry.published.text
            video_info['description'] = entry.media.description.text
            video_info['category'] = entry.media.category[0].text
            video_info['tags'] = entry.media.keywords.text
            video_info['duration_seconds'] = entry.media.duration.seconds
            video_info['view_count'] = entry.statistics.view_count
            video_info['rating'] = entry.rating.average
        except:
            pass
    return video_info

def get_gender_subcondition():
    idx = random.randint(0, 2)
    return [GENDER_LESS, GENDER_NORMAL, GENDER_MORE][idx]

def count_gender_on_page(uri, user_gender):
    video_id = get_id_from_uri(uri)
    gender_subcondition = get_gender_subcondition()
    try:
        ytfeed = app.yts.GetYouTubeVideoCommentFeed(video_id=video_id)
        error_code = None
    except gdata.service.RequestError, inst:
        print 'now video_id = ', video_id
        print 'API ERROR!', inst[0]
        error_code = inst[0]
        return 0, 0, 0, error_code, None, gender_subcondition

    contents = []
    names = []
    for my_e in ytfeed.entry:
        try:
            if my_e.content.text is not None and my_e.author[0].name.text is not None:
                contents.append(my_e.content.text)
                names.append(my_e.author[0].name.text)
        except:
            continue

    comments = zip(names, contents)
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

    if male + female == 0:
        return 0, male, female, error_code, comments, gender_subcondition
    if user_gender == 'Male':
        ratio = male * 1.0 / (male + female)
    elif user_gender == 'Female':
        ratio = female * 1.0 / (male + female)

    s = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0001]
    for i in range(len(s) - 1):
        if ratio >= s[i] and ratio < s[i + 1]:
            scale = i

    if gender_subcondition == GENDER_LESS:
        scale -= 1
    elif gender_subcondition == GENDER_MORE:
        scale += 1

    scale = max(scale, 0)
    scale = min(scale, 4)

    return scale, male, female, error_code, comments, gender_subcondition


def randomly_assign_condition():
    condition_list = ['gender', 'location', 'control']

    #first_category = random.randint(0, len(condition_list) - 1)
    probability = [0.4, 0.6, 0]
    first_category = np.argmax(np.random.multinomial(1, probability))


    return condition_list[first_category]

    """
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
    """

def get_geo():
    t = random.random()
    # distribution is prone towards extream sides
    s = [0, 0.3, 0.45, 0.55, 0.7, 1.00001]
    for i in range(len(s) - 1):
        if t >= s[i] and t < s[i + 1]:
            return i

