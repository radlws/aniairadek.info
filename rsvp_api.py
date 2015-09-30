# import os
from flask import Flask # , redirect, url_for
#from flaskext.mail import Mail
from flask_mail import Mail,Message
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('settings')  # Load from settings.py module

mail = Mail(app)
db = SQLAlchemy(app)

#from  import views, models
#from models import RSVPEntry

@app.route('/')
def hello_world():
    # This route will not be available, only api will be
    return 'Hello World!'

@app.route('/api', methods=['GET', 'POST'])
def new():
    # TODO: configure the email out stuff if req.
    #msg = Message("Hello",
    #              sender="radzhome@radtek.dev",
    #              recipients=["radzhome@gmail.com"])
    #mail.send(msg)

    #rsvp_entry = RSVPEntry(names='One Two Three Names', email='radzhome@gmail.com')
    #db.session.add(rsvp_entry)
    #db.session.commit()

    return 'hello world'

@app.errorhandler(404)
def page_not_found(e):
    # u = request.url_rule
    # return "this page not found %s" % u.rule, 404
    return 'this page not found', 404
    # return flask.redirect('http://aniairadek.info', code=302)
    # return redirect(url_for('hello_world'))

if __name__ == '__main__':
    #app.debug = True
    app.run()
