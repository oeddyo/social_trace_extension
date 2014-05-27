__author__ = 'eddiexie'
from app import app
import mongo

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



collection = mongo.connect("page")

for obj in collection.find():

    url = "https://www.youtube.com/watch?v=" + obj['_id']['page_id']
    try:
        video_info = get_video_info(url)
    except:
        continue

    if 'video_info' not in obj or 'published_on' not in obj['video_info'] or obj['video_info']['published_on'] is None:
        obj['video_info'] = video_info

    collection.save(obj)

