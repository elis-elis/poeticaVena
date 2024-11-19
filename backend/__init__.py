"""
In this setup:
- Migrate Initialization: 
You’re initializing Flask-Migrate by passing both the app and the db to it, which is essential for linking the database and the migration utility.
- Blueprints:
You’re correctly using blueprints for modular routes and registering them within create_app, keeping your application organized.
- App Context:
The use of with app.app_context() ensures that any functions needing the application context, like initialize_poem_types(), can be safely run.
- Database Creation Check:
Calling create_database(app) ensures the database exists when the app is initialized.
- Config and Logging:
Setting up configuration and logging inside create_app makes the code reusable across different environments (development, production).
"""

from flask import Flask, jsonify
import logging
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from .database import db, create_database
from .data_utils import initialize_poem_types
from backend.data_utils import initialize_poem_types
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)

    # CORS(app, origins=["http://localhost:3000"])  # Next.js frontend
    # Allow CORS for the frontend domain
    # CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://your-frontend-domain.com"]}}, supports_credentials=True)
    CORS(app, resources={r"/*": {"origins": "https://poeticavena.onrender.com"}})

    # Swagger-UI config
    SWAGGER_URL = "/api/docs"
    API_URL = "/static/poetica-vena.json"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Poetica Vena API'
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Set the HTTP request/response log level to WARNING or ERROR
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # Configure other aspects of logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app.config.from_object(Config)
    app.config['DEBUG'] = True

    db.init_app(app)

    migrate = Migrate(app, db)  # Bind Migrate to app and db

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
