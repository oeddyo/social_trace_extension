__author__ = 'eddiexie'
import json

from app import app


def post_wapper( service, data_dic):
    data = self.test_app.post(service, data=json.dumps(data_dic),headers={'Content-Type': 'application/json'} ).data
    print 'before tmp, data = ', data
    tmp = json.loads(data)
    print 'OK tmp = ', tmp
    return tmp
    return json.loads(data)

data_dic = {
    'uri': "http://www.youtube.com/watch?v=kffacxfA7G4",
    'user_id': "TEST"
}

response = app.test_client().post('/get_page_config', data=data_dic)



print response