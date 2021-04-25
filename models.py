from sqlalchemy.orm import column_property, backref
from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pw_hash = db.Column(db.String(255), nullable=False)

    # courses = db.relationship('Course', secondary='my_courses', backref='classes')
    courses = db.relationship('Course', secondary='my_courses', viewonly=True)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def toDict(self):
        return{
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'pw_hash': self.email
        }

class MyCourse(db.Model):
    __tablename__ = 'my_courses'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref=backref('my_courses', cascade="all, delete-orphan"))
    course = db.relationship('Course', backref=backref('my_courses', cascade="all, delete-orphan"))
    review = db.relationship('Review', backref='course', lazy=True, uselist=False, cascade="all, delete-orphan")

    def toDict(self):
        return{
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id
        }


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    enjoyability = db.Column(db.Integer, nullable=False)

    mycourse_id = db.Column(db.Integer, db.ForeignKey('my_courses.id'))

    def toDict(self):
        return{
            'id': self.id,
            'mycourse_id': self.mycourse_id,
            'text': self.text,
            'difficulty': self.difficulty,
            'enjoyability': self.enjoyability
        }

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(4), nullable=False)
    num = db.Column(db.String(4), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=0)
    enjoyability = db.Column(db.Integer, nullable=False, default=0)

    course_code = column_property(dept+num)
    
    # employees = db.relationship('Employee', secondary='jobs', backref='teaches')
    employees = db.relationship('Employee', secondary='jobs', viewonly=True)
    # users = db.relationship('User', secondary='my_courses', backref='students')
    users = db.relationship('User', secondary='my_courses', viewonly=True)

    def toDict(self):
        return{
            'id': self.id,
            'dept': self.dept,
            'num': self.num,
            'name': self.name
        }

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(5), nullable=False)
    fname = db.Column(db.String(30), nullable=False)
    sname = db.Column(db.String(30), nullable=False)
    
    # courses = db.relationship('Course', secondary='jobs', backref='employs')
    courses = db.relationship('Course', secondary='jobs', viewonly=True)

    def toDict(self):
        return{
            'id': self.id,
            'title': self.title,
            'fname': self.fname,
            'sname': self.sname
        }

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    position = db.Column(db.String(20), nullable=False)
    
    employee = db.relationship('Employee', backref=backref('jobs', cascade="all, delete-orphan"))
    course = db.relationship('Course', backref=backref('jobs', cascade="all, delete-orphan"))

    def toDict(self):
        return{
            'id': self.id,
            'emp_id': self.emp_id,
            'course_id': self.course_id,
            'position': self.position
        }

