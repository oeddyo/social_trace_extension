
import pymongo
from pymongo import MongoClient


def connect(c_name = 'record'):
    client = MongoClient('ec2-174-129-119-33.compute-1.amazonaws.com')
    db = client['social_trace']
    collection = db[c_name]
    return collection

