from flask import jsonify, request, render_template
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError

from initServer import app, bcrypt, db
from models import User, Course, Employee, Review, MyCourse, Job


''' Set up JWT here '''
def authenticate(uname, password):
    #search for the specified user
    user = User.query.filter_by(username=uname).first()
    #if user is found and password matches
    if user and user.check_password(password):
        return user

#Payload is a dictionary which is passed to the function by Flask JWT
def identity(payload):
    return User.query.get(payload['identity'])

jwt = JWT(app, authenticate, identity)
''' End JWT Setup '''



# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    courses = [course.toDict() for course in courses]
    return jsonify(courses)

# sanity check route
@app.route('/signup', methods=['POST'])
def signup():
    userdata = request.get_json()
    newuser = User(username=userdata['username'], email=userdata['email'])
    newuser.set_password(userdata['password'])
    try:
        db.session.add(newuser)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return 'username or email already exists'
    return 'user created'


if __name__ == '__main__':
    app.run()