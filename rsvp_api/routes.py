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

rsvp_app = Flask(__name__)
# rsvp_app.config.from_object('settings')  # Load from settings.py module
mail = Mail(rsvp_app)

basedir = os.path.abspath(os.path.dirname(__file__))
rsvp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rsvp.db')  # 'sqlite:////tmp/test.db'
rsvp_app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')

db = SQLAlchemy(rsvp_app)
# CORS(rsvp_app)  # allow all origins


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


# ROUTES

@rsvp_app.route('/')
def hello_world():
    # This route will not be available, only api will be
    return 'Hello World!'

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

    rsvp_entry = RSVPEntry(names=names, email=email, attending=attending, no_guests=no_guests)
    db.session.add(rsvp_entry)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(msg="Sorry this email was already used.", success=False)
    except Exception as e:
        logging.error("Something went wrong while writing to db {0}".format(e))

    # Send out an emails
    try:
        body = "Somebody has RSVPed. Names: {names}. Email: {email}. No Guests: {no_guests}. Attending {attending}"
        body = body.format(names=names, email=email, no_guests=no_guests, attending=attending)

        msg = Message("RSVP Request", sender="radzhome@radtek.dev",  body=body,
                      recipients=["radzhome@gmail.com", "annabkatarzyna@gmail.com"], )
        mail.send(msg)

        msg = Message("RSVP Notification", sender="radzhome@radtek.dev",  body="Thank you, your RSVP was received.",
                      recipients=[email, ], )
        mail.send(msg)
    except Exception as e:
        logging.error("Something went wrong while sending emails {0}".format(e))

    return jsonify(success=True, msg="RSVP created successfully")


@rsvp_app.errorhandler(404)
def page_not_found(e):
    # u = request.url_rule
    # return "this page not found %s" % u.rule, 404
    return 'this page not found', 404
    # return flask.redirect('http://aniairadek.info', code=302)
    # return redirect(url_for('hello_world'))

if __name__ == '__main__':
    rsvp_app.run(debug=True)
