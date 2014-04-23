from flask import Flask

app = Flask(__name__)
app.secret_key = 'secret key'
from app import views

import gdata.youtube.service
app.yts = gdata.youtube.service.YouTubeService()



# import gender
import inspect
import os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir)
import predict_gender.genderPredictor as GP
app.gp = GP.genderPredictor()
app.gp.trainAndTest()



print "before"
import lib
print 'testing info', lib.get_video_info("https://www.youtube.com/watch?v=NNihymK_XJA")
