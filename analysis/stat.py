__author__ = 'eddiexie'
from pymongo import MongoClient
import operator
import sys


class Analyst:
    def __init__(self):

        # all records in a list
        self.records = []
        self.get_records()

        # user info
        self.users = {}
        self.get_users()

        # records by user
        self.user_records = self.get_user_records()

    def connect(self, c_name = 'record'):
        client = MongoClient('ec2-174-129-119-33.compute-1.amazonaws.com')
        # Test only on the test database!
        db = client['social_trace']
        collection = db[c_name]
        return collection

    def get_records(self):
        cnt = 0
        for r in self.connect().find():
            if 'time' not in r:
                cnt += 1
            else:
                self.records.append(r)
        print "# of bad records = ", cnt

    def get_users(self):
        for r in self.connect("survey").find():
            self.users[r['user_id']] = r

    def count_records(self):
        print '# of good records ', len(self.records)

    def get_user_records(self):
        dic = {}
        for r in self.records:
            if r['user_id'] in dic:
                dic[r['user_id']].append(r)
            else:
                dic[r['user_id']] = [r]

        for u in self.users:
            if u not in dic:
                dic[u] = []
        return dic

    def compute_sessions(self, session_length = 1800*1000):
        u_dic = self.get_user_records()
        sessions = {}
        for u in self.users:
            if u not in u_dic:
                sessions[u] = []
                continue
            sorted(u_dic[u], key = lambda t:t['time'])
            u_dic[u].append({'time': float("Inf")})
            u_sessions = []
            cur = []
            for i in range(len(u_dic[u])-1):
                if abs(u_dic[u][i]['time'] - u_dic[u][i+1]['time']) > session_length:
                    cur.append(u_dic[u][i])
                    u_sessions.append(cur)
                    cur = []
                else:
                    cur.append(u_dic[u][i])
            sessions[u] = u_sessions

        print 'distribution of session'
        print [len(sessions[u]) for u in self.users]
        """
        for u in self.users:
            print 'u_session length = ', len(sessions[u])
            for session in sessions[u]:
                print len(session),
            print '\n'
        """

    def video_distribution(self):
        print 'video distirbution'
        print [len(self.user_records[u]) for u in self.users]

    def count_like_for_user(self, user):
        cnt = 0
        for r in self.records:
            if r['user_id'] == user and r['like']:
                cnt += 1
        return cnt

    def likes_distribution(self):
        print 'distribution of likes'
        print [self.count_like_for_user(u) for u in self.users]

    def conditions_breakdown(self):
        dic = {}
        for key, value in self.users.items():
            dic[key] = value['condition']

        gender = 0
        location = 0
        control = 0

        for key, value in dic.items():
            if value.startswith('gender'):
                gender += 1
            elif value.startswith("location"):
                location += 1
            else:
                control += 1

        print gender, location, control
    def distribution_of_dwell_time(self):
        print 'Distribution of time in minutes'
        print [r['dwell_time']*1.0/(1000*60) for r in self.records]

    def count_bad_entry(self):
        cnt = 0
        for r in self.records:
            if r['user_id'] is None or r['url'] is None or r['dwell_time'] is None or r['condition'] is None or r['gender']['user_gender'] is None:
                cnt += 1
        print 'Bad entry = ', cnt
analyst = Analyst()
analyst.count_records()
analyst.compute_sessions()

analyst.conditions_breakdown()

analyst.video_distribution()

analyst.likes_distribution()

analyst.distribution_of_dwell_time()
analyst.count_bad_entry()