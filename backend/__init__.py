from flask import Flask, jsonify
import logging
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from .database import db, create_database
from .data_utils import initialize_poem_types
from backend.data_utils import delete_poem_type_by_name, initialize_poem_types, delete_unnecessary_poem_type


def create_app():
    app = Flask(__name__)

    # Set the HTTP request/response log level to WARNING or ERROR
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # Configure other aspects of logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app.config.from_object(Config)
    app.config['DEBUG'] = True

    db.init_app(app)

    from .auth import auth
    from .routes import routes

    jwt = JWTManager(app)

    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)

    with app.app_context():  # Ensure it is within the application context for database operations
        initialize_poem_types()
    
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    return app
