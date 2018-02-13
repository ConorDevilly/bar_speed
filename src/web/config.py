import os

# SQLAlchemy config
SQLALCHEMY_DATABASE_URI = 'mysql://barbell_speed:4UkasFaNcBidrqy2vHew@localhost:3306/barbell_speed'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
# TODO: DO PROPERLY
SECRET_KEY = 'a_secret_key'
DEBUG = True

ALLOWED_EXTENSIONS = set(['txt', 'mp4', 'avi'])


# S3 Config
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
