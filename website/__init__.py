from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from os import path
from .models import db
from .auth import auth



db = SQLAlchemy()
DB_NAME = 'poeticaVENA_db'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    jwt = JWTManager(app)

    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('database now exists! 👑')
            