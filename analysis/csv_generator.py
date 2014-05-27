__author__ = 'eddiexie'


from pymongo import MongoClient
from email.utils import parsedate_tz
import dateutil.parser
from datetime import datetime
from pprint import pprint
import pytz

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

class CSVGenerator():
    def __init__(self):
        self.record_objs = [obj for obj in self.connect('record').find()]
        self.survey_objs = [obj for obj in self.connect('survey').find()]
        self.page_objs = [obj for obj in self.connect('page').find()]

    def connect(self, c_name = 'record'):
        client = MongoClient('ec2-174-129-119-33.compute-1.amazonaws.com')
        # Test only on the test database!
        db = client['social_trace']
        collection = db[c_name]
        return collection

    def search_user(self, user_id):
        for u in self.survey_objs:
            if u['user_id'] == user_id:
                if u['email'].find("test")!=-1 or u['email'].find("mor")!=-1 or u['email'].find("raz")!=-1:
                    return None
                return u
        return None

    def search_page(self, user_id, page_id):
        for p in self.page_objs:
            if p["_id"]['user_id'] == user_id and p['_id']['page_id'] == page_id:
                return p
        return None

    def get_row(self, record_obj):
        user_id = record_obj['user_id']
        user_obj = self.search_user(user_id)

        if user_obj is None:
            return None

        url = record_obj['url']
        if url is None:
            return None

        if url.find("watch")==-1:
            return None

        page_id = get_id_from_uri(record_obj['url'])
        page_obj = self.search_page(user_id, page_id)

        if page_obj is None or \
                        'video_info' not in page_obj or \
                        'duration_seconds' not in page_obj['video_info'] or \
                        page_obj['video_info']['duration_seconds'] is None:
            video_length = None
        else:
            video_length = page_obj['video_info']['duration_seconds']

        if page_obj is None or \
                        'video_info' not in page_obj or \
                        'rating' not in page_obj['video_info'] or \
                        page_obj['video_info']['rating'] is None:
            rating = None
        else:
            rating = page_obj['video_info']['rating']

        if page_obj is None or \
                        'video_info' not in page_obj or \
                        'view_count' not in page_obj['video_info'] or \
                        page_obj['video_info']['view_count'] is None:
            view_count = None
        else:
            view_count = page_obj['video_info']['view_count']

        if page_obj is None or \
                        'video_info' not in page_obj or \
                        'published_on' not in page_obj['video_info'] or \
                        page_obj['video_info']['published_on'] is None:
            published_on = None
        else:
            published_on = page_obj['video_info']['published_on']


        dwell_time = record_obj['dwell_time']*1.0/1000

        if user_id is None:
            return None


        if record_obj['gender'] is None:
            return None

        """
        if record_obj['condition'] in ['gender_more', 'gender_less', 'gender_normal']:
            return None
        """

        user_gender = user_obj['gender']
        user_zip = user_obj['zipcode']

        condition = user_obj['condition']

        if condition.find("gender")!=-1:
            condition = 'gender'

        #judge before or after the change
        if condition == 'gender':
            if 'subcondition' not in record_obj['gender']:
                return None
            else:
                subcondition = record_obj['gender']['subcondition']
        else:
            subcondition = None

        #print 'condition = ', condition, record_obj['gender']
        if condition=='gender' and 'scale' in record_obj['gender']:
            shown_gender_score = record_obj['gender']['scale']
        else:
            shown_gender_score = None

        """
        if shown_gender_score is None or subcondition is None:
            manipulated_gender_score = None
        elif subcondition.find("more")!=-1:
            manipulated_gender_score = shown_gender_score + 1
        elif subcondition.find("less")!=-1:
            manipulated_gender_score = shown_gender_score - 1
        elif subcondition.find("normal")!=-1:
            manipulated_gender_score = shown_gender_score

        if manipulated_gender_score is not None:
            manipulated_gender_score = min(4, manipulated_gender_score)
            manipulated_gender_score = max(0, manipulated_gender_score)
        """

        if condition == 'location':
            display_geo_score = record_obj['geo']
        else:
            display_geo_score = None


        if 'like' in record_obj and record_obj['like'] is not None:
            like = record_obj['like']
        else:
            like = None

        if 'dislike' in record_obj and record_obj['dislike'] is not None:
            dislike = record_obj['dislike']
        else:
            dislike = None


        if 'time' in record_obj and record_obj['time'] is not None:
            time_watched = float(record_obj['time'])/1000.0
            time_watched = datetime.fromtimestamp(time_watched, pytz.utc)
        else:
            time_watched = None

        if published_on is not None and time_watched is not None:
            published_on = dateutil.parser.parse(published_on)
            age_of_video_in_days = (time_watched - published_on).days
        else:
            age_of_video_in_days = None

        obj_fields_list = [
            user_id,
            user_gender,
            user_zip,
            condition,
            subcondition,
            shown_gender_score,
            #manipulated_gender_score,
            display_geo_score,
            video_length,
            dwell_time,
            like,
            dislike,
            rating,
            view_count,
            time_watched.__str__(),
            published_on.__str__(),
            age_of_video_in_days,
            url
        ]


        #pprint(obj_fields_list)
        #print obj_fields_list

        return obj_fields_list


    def get_rows(self):
        res = []
        for record_obj in self.record_objs:
            cur_row = self.get_row(record_obj)
            if cur_row is None:
                continue
            else:
                res.append(cur_row)

        import csv
        with open("output.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'user_gender', 'user_zip', 'condition', 'subcondition', 'shown_gender_score',
                                 'shown_geo_score', 'video_length', 'dwell_time', 'like', 'dislike',
                                'rating', 'view_count', 'time_watched', 'time_published', 'dif_between_watched_published_in_days', 'url'])
            writer.writerows(res)


csv_generator = CSVGenerator()
csv_generator.get_rows()



