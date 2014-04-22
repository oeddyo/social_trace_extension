__author__ = 'eddiexie'
from pymongo import MongoClient
import operator
import sys

def connect(c_name = 'record'):
    client = MongoClient('ec2-174-129-119-33.compute-1.amazonaws.com')

    # Test only on the test database!
    if (sys.argv[0].endswith('nosetests')):
        db = client['test_social_trace']
    else:
        db = client['social_trace']
    collection = db[c_name]
    return collection

dic = {}
for r in connect().find():
    email = r['participant']['email']
    if email in dic:
        dic[email] += 1
    else:
        dic[email] =1


sorted_x = sorted(dic.iteritems(), key=operator.itemgetter(1))


for item in sorted_x:
    print item
