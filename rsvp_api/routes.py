import logging
import os

from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
# from flask.ext.cors import CORS
from flask import request
from flask import jsonify
# from flask import json

from validate_email import validate_email
from flask import render_template

rsvp_app = Flask(__name__)
# rsvp_app.config.from_object('settings')  # Load from settings.py module
mail = Mail(rsvp_app)

basedir = os.path.abspath(os.path.dirname(__file__))
rsvp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rsvp.db')  # 'sqlite:////tmp/test.db'
rsvp_app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')

db = SQLAlchemy(rsvp_app)
# CORS(rsvp_app)  # allow all origins

# LOGGING

logging.basicConfig(filename='/tmp/aniairadek.log',
                    level=logging.INFO,
                    format=('%(asctime)s %(name)s@{0}[%(process)d] '.format(os.getenv('HOSTNAME')) +
                            '%(levelname)-8s %(message)s' + '    [in %(pathname)s:%(funcName)s:%(lineno)d]'),
                    datefmt='%m-%d %H:%M')

# MODELS

from sqlalchemy import func


class RSVPEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_guests = db.Column(db.Integer, unique=False, index=False)
    names = db.Column(db.String(255), index=False, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    attending = db.Column(db.Boolean, unique=False, default=True)
    is_active = db.Column(db.Boolean, unique=False, default=True)
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    modified = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    food_message = db.Column(db.Text, index=False, unique=False)
    address = db.Column(db.Text, index=False, unique=False)

    def __init__(self, names, email, attending=True, no_guests=0, is_active=False, food_message="", address=""):
        self.names = names
        self.email = email
        self.attending = attending
        self.no_guests = no_guests
        self.is_active = is_active
        self.food_message = food_message
        self.address = address

    def __repr__(self):
        return '<RSVPEntry %r>' % self.email


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

# CONSTANTS .. move to config
FROM_EMAIL = "do-not-reply@radtek.dev"
ADMIN_EMAILS = ["radzhome@gmail.com", "annabkatarzyna@gmail.com"]

# ROUTES

# @rsvp_app.route('/')
# def hello_world():
#     # This route will not be available, only api will be
#     return 'Hello World!'


@rsvp_app.route('/api/confirm', methods=['GET'])
def get_confirm():
    email = request.args.get('email', '').replace('%20', '+')
    success = True
    if not email or not validate_email(email):
        message = "Sorry, the email specified was not valid. {}".format(email)
        success = False
    else:
        rsvp = RSVPEntry.query.filter_by(email=email).first()
        if not rsvp:
            message = "Sorry, the RSVP you are looking for was not found."
            success = False
        elif rsvp.is_active:
            message = "RSVP was already confirmed."
            success = False
        else:
            rsvp.is_active = True
            db.session.commit()
            message = "RSVP confirmed!"
    msg = Message("RSVP Request Confirmed", sender=FROM_EMAIL,  body="By {0}".format(email), recipients=ADMIN_EMAILS, )
    mail.send(msg)  # user = RSVPEntry.query.get(5)  # get by id
    return render_template("thank_you.html", success=success, message=message)

# @rsvp_app.route('/test_email', methods=['POST', 'GET'])
# def test_template():
#     logging.info("This is a test...")
#     no_guests = 1
#     names = "Radek, Bartek, Ania, Michal"
#     food_message = "I'm a veggie"
#     email = ADMIN_EMAILS[0]
#     html_email = render_template("rsvp_email.html", no_guests=no_guests, names=names, food_message=food_message)
#     txt_email = render_template("rsvp_email.txt", no_guests=no_guests, names=names, food_message=food_message)
#
#     send_email("Thank you for RSVPing", FROM_EMAIL, [email, ], txt_email, html_email)
#     # send_email("This is a test", FROM_EMAIL, ADMIN_EMAILS, render_template("rsvp_email.txt", name="this is a test"),
#     #            render_template("rsvp_email.html", name="this is a test", follower="ok"))
#     return 'good'

@rsvp_app.route('/api', methods=['POST'])
def post_rsvp():
    logging.info("Entering post rsvp")
    data = request.get_json(force=True)

    email = data.get('email')
    if not email or not validate_email(email):
        return jsonify(msg="Sorry, please provide a valid email.", success=False)
    names = data.get('name')
    if not names:
        return jsonify(msg="Sorry, please provide at least one name.", success=False)

    attending = data.get('attending')
    no_guests = data.get('no_guests')
    
    address = data.get('address')
    food_message = data.get('food_message')

    rsvp_entry = RSVPEntry(names=names, email=email, attending=attending, no_guests=no_guests, 
                           food_message=food_message, address=address)
                           
    db.session.add(rsvp_entry)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(msg="Sorry this email was already used. To change your RSVP, email radzhome@gmail.com",
                       success=False)
    except Exception as e:
        logging.error("Something went wrong while writing to db {0}".format(e))

    # Send out an emails
    try:
        body = "Somebody has RSVPed. Names: {names}. Email: {email}. No Guests: {no_guests}. Attending {attending}." + \
               "Food Message {food_message}. Address {address}."
        body = body.format(names=names, email=email, no_guests=no_guests, attending=attending, 
                           food_message=food_message, address=address)

        msg = Message("RSVP Request", sender=FROM_EMAIL,  body=body, recipients=ADMIN_EMAILS, )
        mail.send(msg)

        html_email = render_template("rsvp_email.html", no_guests=no_guests, names=names, food_message=food_message,
                                     email=email.replace('+', '%20'))  # url encode
        txt_email = render_template("rsvp_email.txt", no_guests=no_guests, names=names, food_message=food_message,
                                    email=email)

        send_email("Thank you for RSVPing", FROM_EMAIL, [email, ], txt_email, html_email)

        #msg = Message("RSVP Notification", sender=FROM_EMAIL,  body="Thank you, your RSVP was received.",
        #              recipients=[email, ], )
        #mail.send(msg)
    except Exception as e:
        logging.error("Something went wrong while sending emails {0}".format(e))

    return jsonify(success=True, msg="RSVP created successfully")


@rsvp_app.errorhandler(404)
def page_not_found(e):
    # u = request.url_rule
    # return "this page not found %s" % u.rule, 404
    return 'This page was not found', 404
    # return flask.redirect('http://aniairadek.info', code=302)
    # return redirect(url_for('hello_world'))

if __name__ == '__main__':
    rsvp_app.run(debug=False)
