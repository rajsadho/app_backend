from main import app, db, User, Course, Employee, Review, MyCourse, Job
print("In initDB")
db.create_all(app=app)

users = []

users.append(User(username="jim", email="jim@jim.com"))
users[0].set_password("jimpass")
users.append(User(username="bob", email="bob@gmail.com"))
users[1].set_password("bobpass")
users.append(User(username="sarah", email="sarah@gmail.com"))
users[2].set_password("sarahpass")
users.append(User(username="mark", email="mark@gmail.com"))
users[3].set_password("markpass")

for user in users:
    db.session.add(user)

courses = []

courses.append(Course(dept="COMP", num=2605, name='Enterprise Database Systems', difficulty=1.5, enjoyability=(4+5)/2))
courses.append(Course(dept="INFO", num=1601, name='Introduction to WWW Programming', difficulty=(5+2)/2, enjoyability=(2+1)/2))
courses.append(Course(dept="INFO", num=2602, name='Web Programming & Technologies'))
courses.append(Course(dept="INFO", num=2604, name='Information Systems Security', difficulty=(5+2)/2, enjoyability=(5+1)/2))

for course in courses:
    db.session.add(course)

teachers = []

teachers.append(Employee(title="Ms.", fname="Karleen", sname="Lall"))
teachers.append(Employee(title="Dr.", fname="Koffka", sname="Khan"))
teachers.append(Employee(title="Dr.", fname="Wayne", sname="Goodridge"))
teachers.append(Employee(title="Mr.", fname="Nicholas", sname="Mendez"))

for teacher in teachers:
    db.session.add(teacher)

jobs = []

jobs.append(Job(employee=teachers[0], course=courses[0], position="Tutor"))
jobs.append(Job(employee=teachers[0], course=courses[1], position="Tutor"))
jobs.append(Job(employee=teachers[1], course=courses[0], position="Lecturer"))
jobs.append(Job(employee=teachers[1], course=courses[3], position="Tutor"))
jobs.append(Job(employee=teachers[2], course=courses[3], position="Lecturer"))
jobs.append(Job(employee=teachers[3], course=courses[1], position="Instructor"))
jobs.append(Job(employee=teachers[3], course=courses[2], position="Instructor"))

for job in jobs:
    db.session.add(job)

reviews = []

reviews.append(Review(text="Was enjoyable", difficulty=2, enjoyability=4))
reviews.append(Review(text="Was hard", difficulty=5, enjoyability=2))
reviews.append(Review(text="I didn't like it", difficulty=2, enjoyability=1))
reviews.append(Review(text="Great time", difficulty=1, enjoyability=5))
reviews.append(Review(text="Never again", difficulty=5, enjoyability=1))
reviews.append(Review(text="Would recommend", difficulty=2, enjoyability=5))

for review in reviews:
    db.session.add(review)

ucourses = []

ucourses.append(MyCourse(user=users[0], course=courses[0], review=reviews[0]))
ucourses.append(MyCourse(user=users[0], course=courses[1], review=reviews[2]))
ucourses.append(MyCourse(user=users[1], course=courses[0], review=reviews[3]))
ucourses.append(MyCourse(user=users[1], course=courses[3], review=reviews[4]))
ucourses.append(MyCourse(user=users[2], course=courses[3], review=reviews[5]))
ucourses.append(MyCourse(user=users[2], course=courses[1], review=reviews[1]))
ucourses.append(MyCourse(user=users[0], course=courses[0]))

db.session.commit()