__author__ = 'eddiexie'

import app as ST
import pymongo
from app import mongo
import json
import copy

class TestViews:
    def __init__(self):
        self.test_user_id = "TEST_USER_ID_SHOULD_NEVER_EXIST"
        self.record_data = {'zipcode': '01123',
                'gender': 'Male',
                'email': 'test_email_address@testdomain.com',
                'user_id': self.test_user_id}
        self.test_app= ST.app.test_client()
        self.test_record_id = "TEST_RECORD_ID_SHOULD_NEVER_EXIST"

    def teardown(self):
        print 'Executing tear down'
        collections = ['survey', 'page', 'record']
        for c in collections:
            db = mongo.connect(c)
            db.remove()

    def test_store_survey(self):
        # ensure every possibility of user condition
        assert('OK' in self.test_app.post('/store_survey', data=self.record_data).data)
        collection = mongo.connect("survey")
        assert(collection.find({'user_id': self.test_user_id}).count() != 0)
        entry = [e for e in collection.find({"user_id": self.test_user_id})][0]
        assert('condition' in entry)
        collection.remove({"user_id": self.test_user_id})

    def test_store_record(self):
        data = {'_id': self.test_record_id }
        assert("OK" in self.test_app.post("/store_record", data=json.dumps(data)).data)


    def test_get_page_config(self):
        collection = mongo.connect('survey')
        data_without_gender = copy.deepcopy(self.record_data)
        del data_without_gender['gender']
        assert('OK' in self.test_app.post("/store_survey", data=data_without_gender).data ) #insert survey without gender
        assert('Need Survey' in
               self.test_app.post("/get_page_config", data = json.dumps({
                   'uri': "http://www.youtube.com/watch?v=kffacxfA7G4",
                   'user_id': self.test_user_id
               })).data
        )

        assert(collection.find({"user_id": self.test_user_id}).count()!=0)
        collection.remove({"user_id": self.test_user_id})

        scales = set()
        # Since it's randomly assign users into three bucket. Thus different bucket should have different behavior
        # in terms of what scale would be for the same page (uri below).
        for times in range(30):
            assert('OK' in self.test_app.post("/store_survey", data=self.record_data).data ) #insert survey without gender
            # now gender is in there. So should return info
            assert('same_gender_scale' in self.test_app.post("/get_page_config", data=json.dumps({
                'uri': "http://www.youtube.com/watch?v=kffacxfA7G4",
                'user_id': self.test_user_id
                })).data
            )
            #second time it will retrival from db directly
            retrivaled_data = json.loads(self.test_app.post("/get_page_config", data=json.dumps({
                'uri': "http://www.youtube.com/watch?v=kffacxfA7G4",
                'user_id': self.test_user_id
            })).data)
            scales.add(retrivaled_data['same_gender_scale'])
            assert (retrivaled_data['_id']['page_id'] == 'kffacxfA7G4')
            assert (retrivaled_data['_id']['user_id'] == self.test_user_id)

            collection.remove({'user_id': self.test_user_id})
            page_collection = mongo.connect("page")
            page_collection.remove()
        assert(len(scales)>=2)

