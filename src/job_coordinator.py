from s3_dao import S3DAO
import os # TODO

class JobCoordinator:
    def __init__(self):
        self.S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
        self.S3_KEY = os.environ.get("S3_ACCESS_KEY")
        self.S3_SECRET = os.environ.get("S3_SECRET_KEY")
        self.S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(self.S3_BUCKET)
        self.s3_dao = S3DAO(self.S3_KEY, self.S3_SECRET)
        self.vid_location = "/tmp/current_video"

    def start(self, vid_path):
        self.s3_dao.download_file_from_s3(
                self.S3_BUCKET,
                vid_path,
                self.vid_location
                )
        # TODO
        os.system("cat {}".format(self.vid_location))
        # TODO: Start tracker on file
        # TODO: Get numbers from tracker
        # TODO: Send numbers to DB
        # TODO: Send SNS notification
