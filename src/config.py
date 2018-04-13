import os

# SQLAlchemy config
SQL_USER = os.environ.get("SQL_USER")
SQL_PASS = os.environ.get("SQL_PASS")
SQL_SERVER = os.environ.get("SQL_SERVER")
SQL_PORT = os.environ.get("SQL_PORT")
SQL_DB = os.environ.get("SQL_DB")
SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}'.format(SQL_USER, SQL_PASS, SQL_SERVER, SQL_PORT, SQL_DB)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'a_secret_key'
DEBUG = True

ALLOWED_EXTENSIONS = set(['mp4', 'avi'])
CLASSIFIER_LOCATION = os.environ.get("CLASSIFIER_LOCATION")


# S3 Config
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
