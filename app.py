#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, current_app, session, redirect
from flask_sqlalchemy import SQLAlchemy
from backend_requests import get_data, process_data, remove_data
from flask.json import jsonify
#from data import X
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from data.insert_resources import insertRes
import pyrebase
import random
from collections import defaultdict
from sqlalchemy import create_engine
import pandas as pd

current_user = {}
ADMIN_EMAIL = "admin@gymtracker.com"

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
config = app.config["API_KEY"]
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
# insert resources
# insertRes(db)


# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/gym')
def bothGym():
    if 'usr' not in session:
        print("\nNot logged in...")
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    all_resources = []
    all_resources.append("Equipment Information")
    all_resources.append(get_data.get_all_resources(db))
    return render_template('pages/gym.html', data=all_resources, loggedIn=userLoggedIn)


@app.route('/brodie')
def brodie():
    return render_template('pages/brodie.html')


@app.route('/logout')
def logout():
    usr = session.pop('usr', None)
    user_email = session.pop('email', None)
    session.pop('uid', None)
    user_name = session.pop('name', None)
    session.pop('isAdmin', None)
    print("Logging user {}, {} out...".format(user_name, user_email))
    return render_template('pages/placeholder.home.html')


@app.route('/brodieEquipment')
def brodieGym():
    if 'usr' not in session:
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    brodie_resources = []
    brodie_resources.append("Brodie Equipment")
    brodie_resources.append(get_data.get_filtered_data(
        db, "*", table="Resources", where="Location = 'Brodie' AND ResourceDisplay = 1"))
    return render_template('pages/gym.html', data=brodie_resources, loggedIn=userLoggedIn)


@app.route('/wilson')
def wilson():
    return render_template('pages/wilson.html')


@app.route('/wilsonEquipment')
def wilsonGym():
    if 'usr' not in session:
        print("\nNot logged in...")
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    wilson_resources = []
    wilson_resources.append("Wilson Equipment")
    wilson_resources.append(get_data.get_filtered_data(
        db, "*", table="Resources", where="Location = 'Wilson' AND ResourceDisplay = 1"))
    return render_template('pages/gym.html', data=wilson_resources, loggedIn=userLoggedIn)


@app.route('/Classes')
def bothClasses():
    if 'usr' not in session:
        print("\nNot logged in...")
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    all_classes = get_data.get_all_classes(db)
    return render_template('pages/classes.html', header="All Classes", data=all_classes, loggedIn=userLoggedIn)


@app.route('/wilsonClasses')
def wilsonClass():
    if 'usr' not in session:
        print("\nNot logged in...")
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    wilson_classes = get_data.get_filtered_classes(
        db, filter_on='ClassLocation', filter_val='Kville')
    return render_template('pages/classes.html', header="Wilson Classes", data=wilson_classes, loggedIn=userLoggedIn)


@app.route('/brodieClasses')
def brodieClass():
    if 'usr' not in session:
        print("\nNot logged in...")
        userLoggedIn = False
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])
        userLoggedIn = True
    wilson_classes = get_data.get_filtered_classes(
        db, filter_on='ClassLocation', filter_val='Brodie')
    return render_template('pages/classes.html', header="Brodie Classes", data=wilson_classes, loggedIn=userLoggedIn)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/profile')
def profile():
    if 'usr' not in session:
        print("\nNot logged in...")
        form = RegisterForm(request.form)
        return render_template('forms/login.html', form=form)
    else:
        print("\nUser is logged in...")
        print("Email:", session['email'])

    user_reservations = get_data.get_user_bookings_for_profile(
        db, session['uid'])
    user_enrollments = get_data.get_user_enrollments_for_profile(
        db, session['uid'])
    return render_template('pages/profile.html', userEmail=session['email'], userDisplayName=session['name'], isAdmin=session['isAdmin'],
                           reservations=user_reservations, enrollments=user_enrollments)


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form, form_error=False)


@app.route('/register', methods=["GET", "POST"])
def signUpCompleted():
    if request.method == "POST":
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmpass = request.form.get('confirm')
        if not process_data.validate_username(username):
            # TODO: display error saying should be only letters. (HTML input regex?)
            print("Invalid user name. Should be only alphabetic...")
            form = RegisterForm(request.form)
            return render_template('forms/register.html', form=form, form_error=True)
        if password != confirmpass:
            # TODO: display error saying passwords don't match?
            form = RegisterForm(request.form)
            return render_template('forms/register.html', form=form, form_error=True)
        if ' ' in email or ';' in email:
            # TODO: display error saying passwords don't match?
            form = RegisterForm(request.form)
            return render_template('forms/register.html', form=form, form_error=True)
        user = auth.create_user_with_email_and_password(email, password)
        process_data.insert_into_users(db, username, email)
        if user is not None:
            # NOTE: if you add more stuff to session during login,
            # then also edit logout to remove that stuff
            user_id = user['idToken']
            session['usr'] = user_id
            user_email = user['email'] if user is not None else None
            session['email'] = user_email
            user_record = get_data.get_user_from_email(db, user_email)
            if user_record is None:
                # NOTE: This means didn't find any users with the email used to log in.
                # Render 404?
                return render_template('errors/404.html')
            session['uid'] = user_record['ID']
            session['name'] = user_record['Name']
            session['isAdmin'] = session['email'] == ADMIN_EMAIL
    return render_template('pages/placeholder.home.html', userInfo=user['idToken'])


@app.route('/login', methods=["GET", "POST"])
def signInCompleted():
    if request.method == "POST":
        email = request.form.get('name')
        password = request.form.get('password')
        user = auth.sign_in_with_email_and_password(email, password)
        if user is not None:
            # NOTE: if you add more stuff to session during login,
            # then also edit logout to remove that stuff
            user_id = user['idToken']
            session['usr'] = user_id
            user_email = user['email'] if user is not None else None
            session['email'] = user_email
            user_record = get_data.get_user_from_email(db, user_email)
            if user_record is None:
                # NOTE: This means didn't find any users with the email used to log in.
                # Render 404?
                return render_template('errors/404.html')
            session['uid'] = user_record['ID']
            session['name'] = user_record['Name']
            session['isAdmin'] = session['email'] == ADMIN_EMAIL
        if user == None:
            form = RegisterForm(request.form)
            return render_template('forms/login.html', form=form)
    return render_template('pages/placeholder.home.html', userInfo=user)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('errors/500.html'), 500


@app.route('/book_available_times/<ResourceID>', methods=['GET', 'POST'])
def book_available_times(ResourceID="0"):
    # print("reached")
    if request.method == "POST":
        dateTime = request.form.get('time').split(",")
        date, time = dateTime[0], dateTime[1]
        # print(time)
        resType = request.form.get('resType')
        valuesDict = {'UserID': str(session['uid']), 'DateBookedOn': date, 'TimeBookedAt': time,
                      'ResourceID': ResourceID, 'ResourceType': resType}
        process_data.insert_into_bookings(db, valuesDict)
        previous_url = request.referrer
        return redirect(previous_url)

    # for GET requests
    where = "ResourceID = {}".format(ResourceID)
    datesBooked = get_data.get_filtered_data(
        db, "DateBookedOn, TimeBookedAt", "Bookings", where)
    ret = process_data.get_available_datetimes(
        datesBooked, "08:00:00", "22:00:00")
    # print(ret)
    return ret


@app.route('/remove_reservation/<itemType>/<itemID>', methods=['POST'])
def remove_reservation(itemType, itemID):
    remove_data.remove_reservation(db, itemType, itemID, session['uid'])
    previous_url = request.referrer
    # print(previous_url)
    return redirect(previous_url)


@app.route('/book_classes/<ResourceID>/<ResourceDate>', methods=['POST'])
def book_classes(ResourceID="0", ResourceDate="00:00:00"):
    # print("reached")
    if request.method == "POST":
        valuesDict = {'UserID': str(session['uid']),
                      'ResourceID': ResourceID, 'DateBookedOn': ResourceDate}
        process_data.insert_into_enrollments(db, valuesDict)
        previous_url = request.referrer
        print(previous_url)
        return redirect(previous_url)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
#if __name__ == '__main__':
 #   port = int(os.environ.get('PORT', 5000))
  #  app.run(host='0.0.0.0', port=port)
'''
