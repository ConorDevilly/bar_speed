from flask import Flask, request, render_template, flash, redirect, url_for, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import boto3, botocore
from config import S3_KEY, S3_SECRET, S3_BUCKET
from models.User import User
from DB import db


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

# Setup Flask Login
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
    return render_template('graphs.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # TODO: Encryption
    # TODO: Add password confirmation checks
    user = User(request.form['username'], request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    # TODO: Encryption
    password = request.form['password']
    registered_user = User.query.filter_by(username=username, password=password).first()
    if registered_user is None:
        flash('Username or password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('upload'))

@app.route('/logout')
def logout():
    logout_user();
    flash('Logged out successfully')
    return redirect(url_for('login'))


# TODO: Revise all this logic
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    if "user_file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["user_file"]
    if file.filename == "":
        flash("No file selected")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
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
    return "{}{}".format(app.config["S3_LOCATION"], file.filename)


if __name__ == '__main__':
    app.run()
