from web.DB import db

class BarDistance(db.Model):
    __tablename__ = "BarDistance"
    vid = db.Column('vid', db.Integer, db.ForeignKey('Video.vid'), primary_key=True)
    vid_frame = db.Column('vid_frame', db.Integer, primary_key=True)
    distance = db.Column('distance', db.Float)

    def __init__(self, vid, vid_frame, distance):
        self.vid = vid
        self.vid_frame = vid_frame
        self.distance = distance

    def __repr__(self):
        return '<BarDistance v:{} f:{} d:{}>'.format(self.vid, self.vid_frame, self.distance)
