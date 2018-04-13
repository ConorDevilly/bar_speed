from cv2 import CascadeClassifier
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker import BarbellTracker
from web.models.Video import Video
from web.models.BarDistance import BarDistance
from web.models.User import User
from s3_dao import S3DAO
import config


class JobCoordinator:
    def __init__(self):
        self.s3_dao = S3DAO(config.S3_KEY, config.S3_SECRET)
        self.db_eng = create_engine(config.SQLALCHEMY_DATABASE_URI)
        self.vid_location = "/tmp/current_video"

    def start(self, vid_path):
        self.tracker = BarbellTracker('')
        self.s3_dao.download_file_from_s3(
            config.S3_BUCKET,
            vid_path,
            self.vid_location
        )
        # Create the classifier to detect the barbell
        classifier = CascadeClassifier(config.CLASSIFIER_LOCATION)
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
