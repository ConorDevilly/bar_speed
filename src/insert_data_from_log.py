import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import web.models
from web.models.BarDistance import BarDistance
from web.models.Video import Video
from web.models.User import User
from plot import BarGraph

parser = argparse.ArgumentParser(description='Insert video data from log file into DB')
parser.add_argument('-l', '--log_file', help='Path to log file', required=True)
parser.add_argument('-v', '--video_id', help='ID of video to associate data with', required=True)
args = parser.parse_args()

# Init app & db
db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object('web.config')
db.init_app(app)

# Load log data
bar_graph = BarGraph()
bar_graph.load_data(args.log_file)

# Insert into db
frame_ctr = 1
with app.app_context():
    for entry in bar_graph.distance_data:
        stat = BarDistance(args.video_id, frame_ctr, entry)
        db.session.add(stat)
        frame_ctr += 1
    db.session.commit()
