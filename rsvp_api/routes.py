import logging

from flask import Flask

from flask_mail import Mail
from flask_mail import Message

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask.ext.cors import CORS

from flask import request
from flask import jsonify
from flask import json

from validate_email import validate_email

rsvp_app = Flask(__name__)
rsvp_app.config.from_object('settings')  # Load from settings.py module

mail = Mail(rsvp_app)
db = SQLAlchemy(rsvp_app)
CORS(rsvp_app)

# from flask_mail import Message
# from sqlalchemy import func

#from models import RSVPEntry

# from rsvp_app import models
# from rsvp_app import views

# from flask.ext.sqlalchemy import SQLAlchemy
# db = SQLAlchemy(app)

# MODELS

from sqlalchemy import func


class RSVPEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(255), index=False, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    is_attending = db.Column(db.Boolean, unique=False, default=True)
    is_active = db.Column(db.Boolean, unique=False, default=True)
    created = db.Column(db.DateTime, nullable=False, server_default=func.now())
    modified = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    food_message = db.Column(db.Text, index=False, unique=False)
    address = db.Column(db.Text, index=False, unique=False)

    def __init__(self, names, email, is_attending=True, is_active=False, food_message="", address=""):
        self.names = names
        self.email = email
        self.is_attending = is_attending
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

#from crossdomain import crossdomain

@rsvp_app.route('/api', methods=['POST'])
def post_rsvp():

    data = request.get_json(force=True)

    email = data.get('email')
    if not email or not validate_email(email):
        return jsonify(msg="Sorry, please provide a valid email.", success=False)
    names = data.get('name')
    if not names:
        return jsonify(msg="Sorry, please provide at least one name.", success=False)

    rsvp_entry = RSVPEntry(names=names, email=email)
    db.session.add(rsvp_entry)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(msg="Sorry this email was already used.", success=False)

    # Send out an emails
    try:
        msg = Message("RSVP Notification", sender="radzhome@radtek.dev",  body="Somebody has RSVPed",
                      recipients=["radzhome@gmail.com", "aniabkatarzyna@gmail.com"], )
        mail.send(msg)

        msg = Message("RSVP Notification", sender="radzhome@radtek.dev",  body="Thank you, your RSVP was received.",
                      recipients=[email, ], )
        mail.send(msg)
    except Exception as e:
        logging.error("Something went wrong while sending emails {}".format(e))

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
