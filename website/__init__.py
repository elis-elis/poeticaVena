from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from config import Config

db = SQLAlchemy()
DB_NAME = 'poeticaVENA_db'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    create_database(app)

    return app

def create_database(app):
    if not path.exists('website'/ + DB_NAME):
        with app.app_context():
            db.create_all()
            print('database now exists! 👑')
