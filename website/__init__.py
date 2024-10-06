from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from .database import db, create_database


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['DEBUG'] = True

    db.init_app(app)

    from .auth import auth
    from .views import views

    jwt = JWTManager(app)

    app.register_blueprint(views, url_prefix='/views')
    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)
    
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        print("Protected route accessed")  # Add this to debug
        print(f'User ID: {current_user}')  # Debug statement
        return jsonify(logged_in_as=current_user), 200

    return app
