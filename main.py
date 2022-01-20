from __future__ import division, print_function
import sys
import os
import keras.models
import numpy as np
from keras.preprocessing import image

from flask import Flask, flash, request, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

db = SQLAlchemy()

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True,  primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(1000), nullable=False)
    last_name = db.Column(db.String(1000), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    phone = db.Column(db. VARCHAR(10), nullable=False)
    medication = db.Column(db.String(1000))
    allergy = db.Column(db.String(1000))


MODEL_PATH = "/web/My_Model/"
model = keras.models.load_model(MODEL_PATH)
model_weights = "/web/modelweights.h5"
model.load_weights(model_weights)


def model_predict(img_path, model):

    IMG = image.load_img(img_path)
    print(type(IMG))

    IMG_ = IMG.resize((224, 224))
    print(type(IMG_))

    IMG_ = np.asarray(IMG_)
    print(IMG_.shape)
    IMG_ = np.true_divide(IMG_, 255)
    IMG_ = IMG_.reshape(1, 224, 224, 3)
    print(type(IMG_), IMG_.shape)

    print(model)
    METRICS = [
        keras.metrics.BinaryAccuracy(name="accuracy"),
        keras.metrics.Precision(name="precision"),
        keras.metrics.Recall(name="recall"),
        keras.metrics.AUC(name="auc"),
    ]

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=3e-4),
        loss=[keras.losses.BinaryCrossentropy(from_logits=False)],
        metrics=METRICS,
    )

    prediction = (model.predict(IMG_) > 0.5).astype("int32")
    return prediction


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    classes = {'train': ['benign', 'malign'],
                'validation': ['benign', 'malign'],
                'test': ['benign', 'malign']}

    if request.method == 'POST':
        f = request.files['file']

        file_path = "/web/uploads/"
        f.save(os.path.join(file_path, secure_filename(f.filename)))

        preds = model_predict(os.path.join(file_path, secure_filename(f.filename)), model)

        print(preds[0])
        np_index = np.array(preds[0])
        predicted_class = classes['train'][np_index[0]]
        print("we think that is {}.".format(predicted_class))
        return str(predicted_class)
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Email sau parola gresita!')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    age = request.form.get('age')
    sex = request.form.get('sex')
    height = request.form.get('height')
    weight = request.form.get('weight')
    phone = request.form.get('phone')
    medication = request.form.get('medication')
    allergy = request.form.get('allergy')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email-ul este deja folosit!')
        return redirect(url_for('signup'))

    new_user = User(email=email,
                    last_name=last_name,
                    password=generate_password_hash(password, method='sha256'),
                    first_name=first_name,
                    age=age,
                    sex=sex,
                    height=height,
                    weight=weight,
                    phone=phone,
                    medication=medication,
                    allergy=allergy)

    db.session.add(new_user)
    db.session.commit()

    flash('Felicitari! Cont creat cu succes!')
    return redirect(url_for('signup'))


@app.route('/profile_predict', methods=['GET'])
def profile_predict():
    return render_template('profile_predict.html')


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    return render_template('profile_predict.html',
                           first_name=current_user.first_name,
                           last_name=current_user.last_name,
                           email=current_user.email,
                           age=current_user.age,
                           sex=current_user.sex,
                           height=current_user.height,
                           weight=current_user.weight,
                           phone=current_user.phone,
                           medication=current_user.medication,
                           allergy=current_user.allergy
                           )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/send_email', methods=['POST', 'GET'])
def send_email():
    if request.method == "POST":
        eemail = request.form.get('mail')
        subject = request.form.get('name')
        msg = request.form.get('message')
        tel = request.form.get('phone')
        date = request.form.get('date')
        medic = request.form.get('doctor')

        message = Message(subject, sender="", recipients=[eemail])

        message.body = "Buna ziua " + subject + ".\n\nAti solicitat o programare cu un doctor in cadrul companiei Skin Cancer Risk Prediction, cu problema urmatoare:\" " + msg + "\". Programarea a fost solicitata in data de " + date + ". Urmeaza sa va contactam la numarul de telefon oferit de dumneavoastra " + tel + ".\n\nVa dorim o zi buna!\nCu respect, Echipa Skin Cancer Risk Prediction."

        mail.send(message)

        flash('Cererea de programare a fost trimisa cu succes! Verificati-va email-ul pentru confirmare.')
        return render_template('profile_predict.html',
                               first_name=current_user.first_name,
                               last_name=current_user.last_name,
                               email=current_user.email,
                               age=current_user.age,
                               sex=current_user.sex,
                               height=current_user.height,
                               weight=current_user.weight,
                               phone=current_user.phone,
                               medication=current_user.medication,
                               allergy=current_user.allergy
                               )


if __name__ == '__main__':
    app.run(debug=True)

