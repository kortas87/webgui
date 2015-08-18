from . import db

class Values5(db.Model):
    __tablename__ = 'values5'
    vid = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.Integer)
    index = db.Column(db.Integer)
    value = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    
    def __repr__(self):
        return self.name


