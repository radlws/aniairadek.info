from rsvp_api import db

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

    def __repr__(self):
        return '<RSVPEntry %r>' % (self.email)

