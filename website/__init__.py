from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from .database import db, create_database
from .auth import auth


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    jwt = JWTManager(app)

    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)
    
    print(f"Connected to database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    return app
