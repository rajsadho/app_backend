from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_jwt import JWT, jwt_required, current_identity
import os
from datetime import timedelta


from models import db, User, Course, Employee, Review, MyCourse, Job


# configuration
DEBUG = True


''' Begin boilerplate code '''
def create_app():
    app = Flask(__name__, static_url_path='')

    uri = os.environ.get('DATABASE_URL')
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 1)

    db.init_app(app)
    return app
''' End Boilerplate Code '''

app = create_app()


app.app_context().push()




# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

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


@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    courses = [course.toDict() for course in courses]
    return jsonify(courses)

@app.route('/courses/<int:id>', methods=['GET'])
def get_course(id):
    course = Course.query.filter_by(id=id).first()
    if not course:
        return jsonify('Course not found'), 404

    teachers = []
    for job in course.jobs:
        teacher = job.employee.toDict()
        teacher['position'] = job.position
        teachers.append(teacher)

    reviews = []
    for ucourse in course.my_courses:
        if ucourse.review:
            reviews.append(ucourse.review.toDict())

    to_send = {'course': course.toDict(), 'teachers': teachers, 'reviews': reviews}
    return jsonify(to_send)

@app.route('/mycourses', methods=['GET'])
@jwt_required()
def get_mycourses():
    mycourses = MyCourse.query.filter_by(user_id=current_identity.id)
    
    to_return = []
    for mycourse in mycourses:
        id = mycourse.id
        course = mycourse.course.toDict()
        if mycourse.review:
            review = mycourse.review.toDict()
        else:
            review = None
        to_return.append({'id': id, 'course': course, 'review': review})

    return jsonify({"mycourses": to_return}), 200


@app.route('/mycourses', methods=['POST'])
@jwt_required()
def add_mycourse():
    coursedata = request.get_json()
    if MyCourse.query.filter_by(course_id=coursedata['course_id'], user_id=current_identity.id).all():
        return jsonify('Course already added'), 409
    course = Course.query.filter_by(id=coursedata['course_id']).first()
    if not course:
        return jsonify('Course not found'), 404
    new_mycourse = MyCourse(user=current_identity, course=course)
    try:
        db.session.add(new_mycourse)
        db.session.commit()
        return jsonify('Course added'), 200
    except:
        db.session.rollback()
        return jsonify('Could not add course'), 500



@app.route('/mycourses/<id>', methods=['DELETE'])
@jwt_required()
def delete_mycourse(id):
    course = MyCourse.query.filter_by(id=id, user_id=current_identity.id).first()
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
@jwt_required()
def get_reviews():
    reviews = []
    for course in current_identity.my_courses:
        if course.review:
            reviews.append(course.review.toDict())

    new_avg = MyCourse.query.join(Review).with_entities(func.avg(Review.enjoyability).filter(MyCourse.course_id==1).label("avg")).scalar()
    print(new_avg, type(new_avg), flush=True)
    new_avg = float(new_avg)
    return jsonify({"reviews": reviews}), 200

@app.route('/myreviews', methods=['POST'])
@jwt_required()
def add_review():
    data = request.get_json()
    check_mycourse = MyCourse.query.filter_by(user_id=current_identity.id, course_id=data['course_id']).first()
    if not check_mycourse:
        return jsonify('Course not in user course list'), 404
    if check_mycourse.review:
        return jsonify('Review exists for course'), 409
    
    review = Review(text=data['text'], difficulty=data['difficulty'], enjoyability=data['enjoyability'])

    try:
        db.session.add(review)
        setattr(check_mycourse, 'review', review)
        db.session.commit()
        
        avg_enjoy = MyCourse.query.join(Review).with_entities(func.avg(Review.enjoyability).filter(MyCourse.course_id==data['course_id']).label("avg")).scalar()
        avg_diff = MyCourse.query.join(Review).with_entities(func.avg(Review.difficulty).filter(MyCourse.course_id==data['course_id']).label("avg")).scalar()
        # print(avg_enjoy, type(new_avg), flush=True)
        avg_enjoy = round(float(avg_enjoy), 1)
        avg_diff = round(float(avg_diff), 1)
        setattr(check_mycourse.course, 'enjoyability', avg_enjoy)
        setattr(check_mycourse.course, 'difficulty', avg_diff)
        db.session.commit()

        return jsonify('Added review'), 200
    except:
        return jsonify("Could not add review"), 500

@app.route('/myreviews/<id>', methods=['PUT'])
@jwt_required()
def edit_review(id):
    review = Review.query.filter_by(id=id).first()
    if not review:
        return jsonify('Review not found'), 404
    if review.course.user_id is not current_identity.id:
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

        avg_enjoy = MyCourse.query.join(Review).with_entities(func.avg(Review.enjoyability).filter(MyCourse.course_id==review.course.course_id).label("avg")).scalar()
        avg_diff = MyCourse.query.join(Review).with_entities(func.avg(Review.difficulty).filter(MyCourse.course_id==review.course.course_id).label("avg")).scalar()
        # print(avg_enjoy, type(new_avg), flush=True)
        avg_enjoy = round(float(avg_enjoy), 1)
        avg_diff = round(float(avg_diff), 1)
        setattr(review.course.course, 'enjoyability', avg_enjoy)
        setattr(review.course.course, 'difficulty', avg_diff)
        db.session.commit()

        return jsonify('Edited review'), 200
    except:
        db.session.rollback()
        return jsonify('Could not edit review'), 500

@app.route('/myreviews/<id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    review = Review.query.filter_by(id=id).first()
    if not review:
        return jsonify('Review not found'), 404
    if review.course.user_id is not current_identity.id:
        return jsonify('Can only edit your reviews'), 403

    try:
        db.session.delete(review)
        db.session.commit()

        avg_enjoy = MyCourse.query.join(Review).with_entities(func.avg(Review.enjoyability).filter(MyCourse.course_id==review.course.course_id).label("avg")).scalar()
        avg_diff = MyCourse.query.join(Review).with_entities(func.avg(Review.difficulty).filter(MyCourse.course_id==review.course.course_id).label("avg")).scalar()
        # print(avg_enjoy, type(new_avg), flush=True)
        avg_enjoy = round(float(avg_enjoy), 1)
        avg_diff = round(float(avg_diff), 1)
        setattr(review.course.course, 'enjoyability', avg_enjoy)
        setattr(review.course.course, 'difficulty', avg_diff)
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

@app.route('/courses/search', methods=['GET'])
def search_results():
    # data = request.get_json()
    query = request.args.get('course')
    if not query:
        return jsonify("Must submit a query"), 404

    results = Course.query.filter(func.lower(Course.course_code).contains(query.lower())).all()
    if results:
        results = [result.toDict() for result in results]
        return jsonify(results), 200

    results = Course.query.filter(func.lower(Course.name).contains(query.lower())).all()

    if not results:
        return jsonify("Course not found"), 404
    else:
        results = [result.toDict() for result in results]
        return jsonify(results), 200



if __name__ == '__main__':
    app.run()