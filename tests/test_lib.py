__author__ = 'eddiexie'


import inspect
import os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)

from app import lib
import random


def test_get_id_from_uri():
    url = "http://www.youtube.com/watch?v=GquEnoqZAK0"
    id = "GquEnoqZAK0"
    assert(id == lib.get_id_from_uri(url))

    url2 = "http://www.youtube.com/watch?v=Q2Niq_v34EI&list=PLzvRx_johoA_Zhuo_pRsWSbARe2IZ2XZJ"
    id2 = "Q2Niq_v34EI"
    assert(id2 == lib.get_id_from_uri(url2))

def test_count_gender_on_page():
    url = "http://www.youtube.com/watch?v=kffacxfA7G4"
    scale, male, female, error_code, _, gender_subcondition = lib.count_gender_on_page(url, 'Male')
    assert(male>0 and female>0)
    scale, male, female, error_code, _, gender_subcondition = lib.count_gender_on_page(url, 'Female')
    assert(male>0 and female>0)


def test_randomly_assign_condition():
    #count = {'gender_more':0, 'gender_less': 0, 'gender_normal':0, 'location':0, 'control':0}
    count = {'gender':0, 'location': 0, 'control': 0}
    for times in range(10000):
        count[lib.randomly_assign_condition()] += 1

    #gender = count['gender_more'] + count['gender_normal'] + count['gender_less']
    gender = count['gender']
    location = count['location']
    control = count['control']

    assert( abs(location-5000)<=1000 and abs(gender-5000)<=1000)


