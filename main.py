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

@app.route('/course/<id>', methods=['GET'])
def get_course(id):
    course = Course.query.filter_by(id=id).first()
    if not course:
        return jsonify('Course not found'), 404

    teachers = [teacher.toDict() for teacher in course.employees]

    reviews = []
    for ucourse in course.my_courses:
        if ucourse.review:
            reviews.append(ucourse.review.toDict())

    to_send = {'teachers': teachers, 'reviews': reviews}
    return jsonify(to_send)

@app.route('/course/<id>', methods=['DELETE'])
def delete_course(id):
    course = Course.query.filter_by(id=id).first()
    if not course:
        return jsonify('Course not found'), 404

    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify('Deleted'), 204
    except Exception as e:
        db.session.rollback()
        return jsonify('Server Error: Could not delete resource'), 500

@app.route('/mycourses/<id>', methods=['DELETE'])
def delete_mycourse(id):
    course = MyCourse.query.filter_by(id=id).first()
    if not course:
        return jsonify('Course not found'), 404

    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify(''), 204
    except:
        db.session.rollback()
        return jsonify('Server Error: Could not delete resource'), 500


@app.route('/teachers', methods=['GET'])
def get_teachers():
    employees = Employee.query.all()
    employees = [employee.toDict() for employee in employees]
    return jsonify(employees)

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