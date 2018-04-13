from web.DB import db


class Video(db.Model):
    __tablename__ = "Video"
    vid = db.Column('vid', db.Integer, primary_key=True)
    uid = db.Column('uid', db.Integer, db.ForeignKey('User.uid'), nullable=False)
    rpe = db.Column('rpe', db.Integer, nullable=True)
    weight = db.Column('weight', db.Float, nullable=True)
    s3_path = db.Column('s3_path', db.String, unique=True, nullable=False)
    fps = db.Column('fps', db.Float, nullable=False)
    cm_multiplier = db.Column('cm_multiplier', db.Float, nullable=False)
    distances = db.relationship('BarDistance', backref='video', lazy=True)

    def __init__(self, uid, rpe, weight, s3_path):
        self.uid = uid
        self.rpe = rpe
        self.weight = weight
        self.s3_path = s3_path
