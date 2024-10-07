from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from .database import db, create_database
from .data_utils import initialize_poem_types


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['DEBUG'] = True

    db.init_app(app)

    from .auth import auth
    from .routes import routes

    jwt = JWTManager(app)

    app.register_blueprint(routes, url_prefix='/routes')
    app.register_blueprint(auth, url_prefix='/auth')

    create_database(app)

    with app.app_context():
        initialize_poem_types()
    
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    return app
