from pymongo import MongoClient
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

