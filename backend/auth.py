from flask import Blueprint, request, jsonify
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .models import Poet
from .schemas import PoetCreate
from datetime import timedelta
from pydantic import ValidationError


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    """
    Poets can log in with their email and password. 
    If not, appropriate error messages are shown.
    """
    data = request.get_json()   # Get JSON data from request body
    # Extract email and password from the request data
    email = data.get('email')
    password = data.get('password')

    # Find poet by email
    poet = Poet.query.filter_by(email=email).first()
    if poet and check_password_hash(poet.password_hash, password):
        access_token = create_access_token(identity=poet.id, expires_delta=timedelta(hours=1))
        print(f'Poet(esse) {poet.poet_name} logged in successfully!')  # Debug statement
        return jsonify(access_token=access_token, token_type="bearer"), 200
    
    else:
        print(f'Failed login attempt for {email}')  # Debug statement
        return jsonify({"error": "Invalid email or password. 🪭 "}), 401
    

@auth.route('/logout', methods=['POST'])
def logout():
    """
    Logs the user out and returns JSON response.
    """
    return jsonify({'message': 'Logged out successfully! 🌈'}), 200


@auth.route('/register', methods=['POST'])
def register():
    """
    New poets can register for an account after passing validation checks. 
    Their password is hashed, and account is saved to the database.
    """

    # Retrieve JSON data from request body
    poet_data = request.json

    # Validate using Pydantic model
    try:
        poet_create = PoetCreate(**poet_data)
    except ValidationError as e:
        # Collect validation errors and return them as a JSON response
        return jsonify({'errors': e.errors()}), 400

    # Step 1: Check if the email already exists
    existing_poet = Poet.query.filter_by(email=poet_create.email).first()
    if existing_poet:
        return jsonify({'error': 'Email already exists. 🥝'}), 409  # Conflict error
        
    # Step 2: Hash the password
    hashed_password = generate_password_hash(poet_create.password)

    # Step 3: Create new poet and save to the database
    new_poet = Poet(
            poet_name=poet_create.poet_name,
            email=poet_create.email,
            password_hash=hashed_password
        )
    db.session.add(new_poet)

    try:
        db.session.commit()
        print('Poet(esse) registered and committed to the database.')  # Debug statement
        return ({'id': new_poet, 'poet_name': new_poet.poet_name, 'email': new_poet.email}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error during registration commit: {e}")  # Debug statement
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
