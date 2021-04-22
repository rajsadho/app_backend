from sqlalchemy.orm import column_property
import datetime

from initServer import bcrypt, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.pw_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(pw_hash, password)

    def toDict(self):
        return{
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'pw_hash': self.email
        }

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(4), nullable=False)
    num = db.Column(db.String(4), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    course_code = column_property(dept+num)

    def toDict(self):
        return{
            'id': id,
            'dept': dept,
            'num': num,
            'name': name
        }

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)


