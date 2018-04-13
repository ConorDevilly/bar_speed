from cv2 import CascadeClassifier
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker import BarbellTracker
from web.models.Video import Video
from web.models.BarDistance import BarDistance
from web.models.User import User
from s3_dao import S3DAO


class JobCoordinator:
    def __init__(self):
        self.S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
        self.S3_KEY = os.environ.get("S3_ACCESS_KEY")
        self.S3_SECRET = os.environ.get("S3_SECRET_KEY")
        self.S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(self.S3_BUCKET)
        self.s3_dao = S3DAO(self.S3_KEY, self.S3_SECRET)
        self.vid_location = "/tmp/current_video"
        self.CLASSIFIER_LOCATION = os.environ.get("CLASSIFIER_LOCATION")
        # TODO: Get from config
        SQL_USER = os.environ.get("SQL_USER")
        SQL_PASS = os.environ.get("SQL_PASS")
        SQL_SERVER = os.environ.get("SQL_SERVER")
        SQL_PORT = os.environ.get("SQL_PORT")
        SQL_DB = os.environ.get("SQL_DB")
        SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(SQL_USER, SQL_PASS, SQL_SERVER, SQL_PORT, SQL_DB)
        self.db_eng = create_engine(SQLALCHEMY_DATABASE_URI)

    def start(self, vid_path):
        self.tracker = BarbellTracker('')
        self.s3_dao.download_file_from_s3(
            self.S3_BUCKET,
            vid_path,
            self.vid_location
        )
        # Create the classifier to detect the barbell
        classifier = CascadeClassifier(self.CLASSIFIER_LOCATION)
        # Load the video into the tracker
        self.tracker.load_video(self.vid_location)
        # Get the FPS of the video
        fps = self.tracker.get_video_fps()
        # Apply the classifier to the video
        frame, pos, cm_multiplier = self.tracker.detect_barbell_pos(classifier)
        # Track the detected objcet throughout the video
        dist_list = self.tracker.track(frame, pos)
        # Add results to the DB
        Session = sessionmaker(bind=self.db_eng)
        db_session = Session()
        video = db_session.query(Video).filter_by(s3_path=vid_path).first()
        # Update the video to add attributes determined by the tracker
        video.fps = fps
        video.cm_multiplier = cm_multiplier
        dist_ctr = 1
        for distance in dist_list:
            bar_distance = BarDistance(video.vid, dist_ctr, distance)
            db_session.add(bar_distance)
            dist_ctr += 1
        db_session.commit()
