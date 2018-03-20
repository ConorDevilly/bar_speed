from flask import Flask, request, render_template, flash, redirect, url_for, g
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import boto3
from config import S3_KEY, S3_SECRET
from models.User import User
from models.Video import Video
from models.BarDistance import BarDistance
from models.VelocityPercentChart import VelocityPercentChart
from DB import db
from numpy import mean
from sqlalchemy.sql import text
from math import floor


# Create flask app and extensions
app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/graphs', methods=['GET'])
def graphs():
    video_list = Video.query.filter_by(uid=current_user.id)
    return render_template('graphs.html', video_list=video_list)


@app.route('/graphs/<int:vid>', methods=['GET'])
def graph_vid(vid):
    # TODO: Can extend other better better?
    # TODO: Add auth for uid assoc w/t vid
    video_list = Video.query.filter_by(uid=current_user.id)
    video = Video.query.filter_by(vid=vid).first()
    vid_dist_data = BarDistance.query.filter_by(vid=video.vid)
    vid_speed_data = []
    reps = 1 # TODO
    prev_dist = 0
    for entry in vid_dist_data:
        curr_dist = entry.distance * video.cm_multiplier
        dist_dif = (curr_dist - prev_dist)
        vid_speed_data.append(abs(dist_dif))
        prev_dist = curr_dist

    average_speed = str(round(mean(vid_speed_data), 2))
    percent_result = db.engine.execute(text(
                                "SELECT percent FROM VelocityPercentChart WHERE reps = :reps ORDER BY ABS( velocity - :average_speed ) LIMIT 1;"
                            ),
                            {'reps': reps, 'average_speed': average_speed}
                        );
    percent_multiplier = percent_result.fetchone()['percent']
    max_prediction = video.weight / (percent_multiplier / float(100))
    max_prediction = max_prediction - (max_prediction % 2.5)

    vid_data = {
            'id': video.vid,
            'dist_data': vid_dist_data,
            'speed_data': vid_speed_data,
            'fps': video.fps,
            'weight': video.weight,
            'cm_multiplier': video.cm_multiplier,
            'average_speed': average_speed,
            'max_prediction': max_prediction
    }
    return render_template('graphs.html', video_list=video_list, vid_data=vid_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # TODO: Add password confirmation checks
    username = request.form['username']
    password = bcrypt.generate_password_hash(request.form['password'])
    email = request.form['email']
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    submitted_password = request.form['password']
    registered_user = User.query.filter_by(username=username).first()
    pw_correct = bcrypt.check_password_hash(registered_user.password, submitted_password)
    if registered_user is None or not pw_correct:
        flash('Username or password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('upload'))


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))


# TODO: Revise all this logic
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # Upload file to S3
    if "user_file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["user_file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        upload_file_to_s3(file, app.config["S3_BUCKET"])
        # Create entry in DB
        # TODO: Refactor video creation into own method
        # TODO: Need to process video after uploading then add to database
        # TODO: IE: Move this till after processing is done
        s3_path = 'videos/' + str(g.user.id) + file.filename
        video = Video(g.user.id, None, request.form['weight'], s3_path)
        db.session.add(video)
        db.session.commit()
        flash("File uploaded successfully")
    else:
        flash("Error uploading file")

    return redirect(url_for('upload'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def upload_file_to_s3(file, bucket_name):
    s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    try:
        s3.upload_fileobj(
                file,
                bucket_name,
                file.filename
        )
    except Exception as e:
        raise(e)


if __name__ == '__main__':
    app.run()
