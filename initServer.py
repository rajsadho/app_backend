from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

# configuration
DEBUG = True

''' Begin boilerplate code '''
def create_app():
    app = Flask(__name__, static_url_path='')

    uri = os.environ.get("DATABASE_URL")  # or other relevant config var 
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7)
    db.init_app(app)
    return app
''' End Boilerplate Code '''

app = create_app()

app.app_context().push()

# instantiate bcrypt
bcrypt = Bcrypt(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})