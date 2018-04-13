from flask import Flask, request, render_template, flash, redirect, url_for, g
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from s3_dao import S3DAO
from web.DB import db
from sqlalchemy.sql import text
from config import S3_BUCKET, S3_KEY, S3_SECRET
from web.models.User import User
from web.models.Video import Video
from web.models.BarDistance import BarDistance


# Create flask app and extensions
app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s3_dao = S3DAO(S3_KEY, S3_SECRET)


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


@app.route('/graphs/<int:vid>', methods=['GET', 'DELETE'])
def graph_vid(vid):
    video = Video.query.filter_by(vid=vid).first()
    if(video is None):
	return render_template('403.html'), 403
    elif(current_user.id != video.uid):
	return render_template('404.html'), 404
    if request.method == 'GET':
	    vid_data = _generate_vid_data(vid)
	    video_list = Video.query.filter_by(uid=current_user.id)
	    return render_template('graphs.html', video_list=video_list, vid_data=vid_data)
    elif request.method == 'DELETE':
	    _delete_vid(vid)
	    return redirect(url_for('graphs')), 200

def _delete_vid(vid):
    # Remove entry from DB
    video = Video.query.filter_by(vid=vid).first()
    s3_path = video.s3_path
    BarDistance.query.filter_by(vid=vid).delete()
    Video.query.filter_by(vid=vid).delete()
    db.session.commit()
    # Remove file from S3
    s3_dao.delete_file_in_s3(S3_BUCKET, s3_path)

def _generate_vid_data(vid):
    video = Video.query.filter_by(vid=vid).first()
    vid_dist_data = BarDistance.query.filter_by(vid=video.vid)
    vid_speed_data = []
    vid_acceleration_data = []
    average_speed = 0
    max_prediction = 0

    # Check processing has worked before attempting to calculate values
    if video.fps is not None:
	    # Generate speed by taken distances every second
	    dist_data = [entry.distance for entry in vid_dist_data]
	    total_seconds = len(dist_data) / video.fps
	    prev_dist = 0
	    for i in xrange(0, int(total_seconds)):
		second = int(i * video.fps)
		curr_dist = dist_data[second] * video.cm_multiplier
		speed = abs(curr_dist - prev_dist)
		vid_speed_data.append(speed)
		prev_dist = curr_dist

	    # Generate acceleration data
	    prev_speed = 0
	    for entry in vid_speed_data:
		vid_acceleration_data.append(abs(entry - prev_speed))
		prev_speed = entry
	    total_dist = abs(max(dist_data) - min(dist_data)) * 2
	    average_speed = (total_dist * video.cm_multiplier) / total_seconds
	    reps = 1 # TODO: Hardcoded reps. Need to create way of detecting multiple reps
	    percent_result = db.engine.execute(text(
					"SELECT percent FROM VelocityPercentChart WHERE reps = :reps ORDER BY ABS( velocity - :average_speed ) LIMIT 1;"
				    ),
				    {'reps': reps, 'average_speed': average_speed * 0.01  }
				);
	    percent_multiplier = percent_result.fetchone()['percent']
	    max_prediction = video.weight / (percent_multiplier / float(100))
	    max_prediction = max_prediction - (max_prediction % 2.5)

    vid_data = {
            'id': video.vid,
            'dist_data': vid_dist_data,
            'speed_data': vid_speed_data,
            'acceleration_data': vid_acceleration_data,
            'fps': video.fps,
            'weight': video.weight,
	    's3_path': video.s3_path,
            'cm_multiplier': video.cm_multiplier,
            'average_speed': average_speed,
            'max_prediction': max_prediction
    }
    return vid_data

@app.route('/register', methods=['POST'])
def register():
    username = request.form['r_username']
    password = bcrypt.generate_password_hash(request.form['r_password'])
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
    pw_correct = False
    if registered_user is not None:
        pw_correct = bcrypt.check_password_hash(registered_user.password, submitted_password)
    if registered_user is None or not pw_correct:
        flash('Username or password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('graphs'))


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))


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
	# Upload to S3
        file.filename = secure_filename(file.filename)
        s3_path = 'videos/' + str(g.user.id) + '/' + file.filename
        s3_dao.upload_file_to_s3(file, app.config["S3_BUCKET"], s3_path)
	# Add video entry to the DB
        video = Video(g.user.id, None, request.form['weight'], s3_path)
        db.session.add(video)
        db.session.commit()
        flash("File uploaded successfully")
    else:
        flash("Error uploading file")

    return redirect(url_for('graphs'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


if __name__ == '__main__':
    app.run('0.0.0.0')
