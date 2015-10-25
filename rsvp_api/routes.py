"""rsvp api, keep py 2.6x compatible"""
import logging
import unicodedata
import os

from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
# from flask.ext.cors import CORS
from flask import request
from flask import jsonify

from validate_email import validate_email
from flask import render_template

rsvp_app = Flask(__name__)

# Does not work for email settings, dunno why
#rsvp_app.config.from_object('settings')  # Load from settings.py module

try:
    from settings_local import MAIL_SERVER
    from settings_local import MAIL_PORT
    from settings_local import MAIL_USE_TLS
    from settings_local import MAIL_USERNAME
    from settings_local import MAIL_PASSWORD
    from settings_local import DEFAULT_MAIL_SENDER
except ImportError:
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = MAIL_PASSWORD = DEFAULT_MAIL_SENDER = None

rsvp_app.config['MAIL_SERVER'] = MAIL_SERVER
rsvp_app.config['MAIL_PORT'] = MAIL_PORT
rsvp_app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
rsvp_app.config['MAIL_USERNAME'] = MAIL_USERNAME
rsvp_app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
rsvp_app.config['DEFAULT_MAIL_SENDER'] = DEFAULT_MAIL_SENDER

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
    # A rsvp email sent would be nice.. but an entry means it has been sent...

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


logging.info("Starting rsvp api")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

# CONSTANTS .. move to config
FROM_EMAIL = "do-not-reply@aniairadek.info" # 'radtek.do.not.reply@gmail.com'  # "do-not-reply@aniairadek.info"
ADMIN_EMAILS = ["radzhome@gmail.com", "annabkatarzyna@gmail.com"]


# TODO: login required views

# ROUTES

@rsvp_app.route('/api/check')
def api_check():
    """Performs check."""
    return 'running'


# @rsvp_app.route('/update_rsvp/<email>', methods=['GET', 'POST'])
# def update_rsvp(email):
#     if request.method == 'GET':
#         pass
#     if request.method == 'POST':
#         pass
#     return 'todo template'
    
    
@rsvp_app.route('/send_rsvp_emails', methods=['GET'])
def send_rsvps():
    """Local use, sends emails to everyone"""
    users = RSVPEntry.query.all()
    sent_to = ""
    for u in users:
        if not u.is_active:
            html_email = render_template("rsvp_email.html", no_guests=u.no_guests, names=u.names,
                                         food_message=u.food_message,
                                         email=u.email.replace('+', '%2B'))  # url encode
            txt_email = render_template("rsvp_email.txt", no_guests=u.no_guests, names=u.names,
                                        food_message=u.food_message,
                                        email=u.email)
            logging.info("Attempting to send email to {0}".format(u.email))
            sent_to += u.email + " "
            send_email("Thank you for RSVPing", FROM_EMAIL, [u.email, ], txt_email, html_email)

    return jsonify(success=True, msg="RSVPs all sent to {0}".format(sent_to))


# Using this route, makes everything time out at times, why??
@rsvp_app.route('/send_invite_emails', methods=['GET'])
def send_invites():
    """Local use, sends emails to everyone"""
    
    logging.info("Entering entering send invites")
    
    try:
        emails = request.args.getlist('email')

        sent_to = ''
        for email in emails:
            html_email = render_template("invite_email.html")  # , name=u['name'])  # url encode
            txt_email = render_template("invite_email.txt")  # , name=u['name'])
            logging.info("Attempting to send email to {0}".format(email))
            sent_to += email + " "
            send_email("Anna & Radek Wedding Invitation", FROM_EMAIL, [email, ], txt_email, html_email)
    except Exception as e:
        logging.error("Something went wrong while sending invite emails {0} 10}".format(e.__class__, e))
        
    return jsonify(success=True, msg="RSVPs all sent to {0}".format(sent_to))

@rsvp_app.route('/api/confirm', methods=['GET'])
def get_confirm():
    logging.info("Entering entering get rsvp confirm")
    
    email = request.args.get('email', '').replace('%2B', '+')  # %40 = @
    success = True
    if not email or not validate_email(email):
        message = "Sorry, the email specified was not valid."  # {0}".format(email)
        success = False
    else:
        rsvp = RSVPEntry.query.filter_by(email=email).first()
        if not rsvp:
            message = "Sorry, the RSVP you are looking for was not found."
            success = False
        elif rsvp.is_active:
            message = "RSVP was already confirmed in the past."
        else:
            rsvp.is_active = True
            db.session.commit()
            message = "RSVP confirmed!"
    msg = Message("RSVP Request Confirmed", sender=FROM_EMAIL,  body="By {0}".format(email), recipients=ADMIN_EMAILS, )
    mail.send(msg)  # user = RSVPEntry.query.get(5)  # get by id
    # Send invite email or no need...
    return render_template("thank_you.html", success=success, message=message)



@rsvp_app.route('/api/rsvp', methods=['POST'])  # Change to /api/rsvp
def post_rsvp():
    logging.info("Entering post rsvp")
    data = request.get_json(force=True)

    # unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    
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
    
    address = unicodedata.normalize('NFKD', address).encode('ascii', 'ignore')
    food_message = unicodedata.normalize('NFKD', food_message).encode('ascii', 'ignore')
    names = unicodedata.normalize('NFKD', names).encode('ascii', 'ignore')
    
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
                                     email=email.replace('+', '%2B'))  # url encode
        txt_email = render_template("rsvp_email.txt", no_guests=no_guests, names=names, food_message=food_message,
                                    email=email)

        send_email("Thank you for RSVPing", FROM_EMAIL, [email, ], txt_email, html_email)

    except Exception as e:
        logging.error("Something went wrong while sending emails {0} 10}".format(e.__class__, e))
    logging.info("Created and sent rsvp email to {0}".format(email))
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
