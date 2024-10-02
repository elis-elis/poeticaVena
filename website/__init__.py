from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'poeticaVENA_db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_is_secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://elisnothing:1234@localhost:5432/{DB_NAME}'
    db.init_aoo(app)

    

    return app

def create_database(app):
    if not path.exists('website'/ + DB_NAME):
        with app.app_context():
            db.create_all()
            print('database now exists! 👑')
            