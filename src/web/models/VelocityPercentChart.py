from web.DB import db


class VelocityPercentChart(db.Model):
    __tablename__ = "VelocityPercentChart"
    reps = db.Column('reps', db.Integer, primary_key=True)
    velocity = db.Column('velocity', db.Float, primary_key=True)
    percent = db.Column('percent', db.Integer)

    def __init__(self, reps, velocity, percent):
        self.reps = reps
        self.velocity = velocity
        self.percent = percent
