from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
# from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import os

# from initServer import app, db, login_manager
from models import db, User, Course, Employee, Review, MyCourse, Job


# ''' Set up JWT here '''
# def authenticate(uname, password):
#     #search for the specified user
#     user = User.query.filter_by(username=uname).first()
#     #if user is found and password matches
#     if user and user.check_password(password):
#         return user

# #Payload is a dictionary which is passed to the function by Flask JWT
# def identity(payload):
#     return User.query.get(payload['identity'])

# jwt = JWT(app, authenticate, identity)
# ''' End JWT Setup '''


# configuration
DEBUG = True

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

''' End Flask Login Functions '''

''' Begin boilerplate code '''
def create_app():
    app = Flask(__name__, static_url_path='')

    uri = os.environ.get('DATABASE_URL')
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    # app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7)
    login_manager.init_app(app)
    db.init_app(app)
    return app
''' End Boilerplate Code '''

app = create_app()

app.app_context().push()


# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


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

@app.route('/login', methods=['POST'])
def loginAction():
    data = request.get_json()
    user = User.query.filter_by(username = data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user) # login the user
        return jsonify('Logged in'), 200

    return jsonify('Invalid credentials'), 401

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify('Logged Out'), 200

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
@login_required
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

@app.route('/mycourses', methods=['GET'])
@login_required
def get_mycourses():
    mycourses = MyCourse.query.filter_by(user_id=current_user.id)
    
    to_return = []
    for mycourse in mycourses:
        id = mycourse.id
        course = mycourse.course.toDict()
        if mycourse.review:
            review = mycourse.review.toDict()
        else:
            review = None
        to_return.append({'id': id, 'course': course, 'review': review})

    return jsonify(to_return), 200


@app.route('/mycourses', methods=['POST'])
@login_required
def add_mycourse():
    coursedata = request.get_json()
    if MyCourse.query.filter_by(course_id=coursedata['course_id'], user_id=current_user.id).all():
        return jsonify('Course already added'), 409
    course = Course.query.filter_by(id=coursedata['course_id']).first()
    if not course:
        return jsonify('Course not found'), 404
    new_mycourse = MyCourse(user=current_user, course=course)
    try:
        db.session.add(new_mycourse)
        db.session.commit()
        return jsonify('Course added'), 200
    except:
        db.session.rollback()
        return jsonify('Could not add course'), 500



@app.route('/mycourses/<id>', methods=['DELETE'])
@login_required
def delete_mycourse(id):
    course = MyCourse.query.filter_by(id=id, user_id=current_user.id).first()
    if not course:
        return jsonify('Course not found'), 404
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify(''), 204
    except:
        db.session.rollback()
        return jsonify('Server Error: Could not delete resource'), 500

@app.route('/myreviews', methods=['GET'])
@login_required
def get_reviews():
    reviews = []
    for course in current_user.my_courses:
        if course.review:
            reviews.append(course.review.toDict())

    return jsonify({"reviews": reviews}), 200

@app.route('/myreviews', methods=['POST'])
@login_required
def add_review():
    data = request.get_json()
    check_mycourse = MyCourse.query.filter_by(user_id=current_user.id, course_id=data['course_id']).first()
    if not check_mycourse:
        return jsonify('Course not in user course list'), 404
    if check_mycourse.review:
        return jsonify('Review exists for course'), 409
    
    review = Review(text=data['text'], difficulty=data['difficulty'], enjoyability=data['enjoyability'])

    try:
        db.session.add(review)
        setattr(check_mycourse, 'review', review)
        db.session.commit()
        return jsonify('Added review'), 200
    except:
        return jsonify("Could not add review"), 500

@app.route('/myreviews/<id>', methods=['PUT'])
@login_required
def edit_review(id):
    review = Review.query.filter_by(id=id).first()
    if not review:
        return jsonify('Review not found'), 404
    if review.course.user_id is not current_user.id:
        return jsonify('Can only edit your reviews'), 403

    data = request.get_json()

    if 'text' in data:
        review.text = data['text']
    if 'difficulty' in data:
        review.difficulty = data['difficulty']
    if 'enjoyability' in data:
        review.enjoyability = data['enjoyability']

    try:
        db.session.add(review)
        db.session.commit()
        return jsonify('Edited review'), 200
    except:
        db.session.rollback()
        return jsonify('Could not edit review'), 500

@app.route('/myreviews/<id>', methods=['DELETE'])
@login_required
def delete_review(id):
    review = Review.query.filter_by(id=id).first()
    if not review:
        return jsonify('Review not found'), 404
    if review.course.user_id is not current_user.id:
        return jsonify('Can only edit your reviews'), 403

    try:
        db.session.delete(review)
        db.session.commit()
        return jsonify('Review deleted'), 200
    except:
        db.session.rollback()
        return jsonify("Could not delete review"), 500    

@app.route('/teachers', methods=['GET'])
def get_teachers():
    employees = Employee.query.all()
    employees = [employee.toDict() for employee in employees]
    return jsonify(employees)


if __name__ == '__main__':
    app.run()