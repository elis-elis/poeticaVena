from flask import Blueprint, request, jsonify, make_response
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    unset_jwt_cookies
)
from .models import Poet
from .schemas import PoetCreate, PoetResponse
from datetime import timedelta
from pydantic import ValidationError
from .poet_utils import get_current_poet


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    """
    Handles the authentication of poets by validating email and password. 
    It generates both an access token and a refresh token using JWT.
    """
    data = request.get_json()   # Get JSON data from request body
    # Extract email and password from the request data
    email = data.get('email')
    password = data.get('password')

    # Find poet by email
    poet = Poet.query.filter_by(email=email).first()
    if poet and check_password_hash(poet.password_hash, password):
        # access_token = create_access_token(identity={'poet_id': poet.id}, expires_delta=timedelta(hours=1))
        access_token = create_access_token(identity={'poet_id': poet.id})
        print(f"DEBUG: Generated token identity -> poet_id: {poet.id}")
        
        refresh_token = create_refresh_token(identity={'poet_id': poet.id})

        # Create a response with the access token in the body
        response = make_response(jsonify(access_token=access_token, refresh_token=refresh_token, token_type="bearer"), 200)

        # Set the refresh token in an HTTP-only cookie
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax'  # Controls when the cookie is sent
        )

        print(f'Poet(esse) {poet.poet_name} logged in successfully! 🚀')  # Debug statement
        return response

    print(f'Failed login attempt for {email}')  # Debug statement
    return jsonify({"error": "Invalid email or password. 🪭 "}), 401


@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Generate a new access token using the refresh token.
    This will allow poets to use their refresh token to get a new access token 
    when the previous one has expired, enabling smooth and continuous authentication 
    without forcing the poet to log in repeatedly.
    """
    # Fetch the poet by email to get the poet_id (using the function we created)
    poet = get_current_poet()
    if not poet:
        return jsonify({'error': 'Poet(esse) not found. 🌴'}), 404

    # Generate a new access token with both poet_id and email in the identity
    new_access_token = create_access_token(identity={'poet_id': poet.id}, expires_delta=timedelta(hours=1))

    return jsonify(access_token=new_access_token), 200


@auth.route('/logout', methods=['POST'])
def logout():
    """
    Logs the user out by clearing the refresh token cookie and unsetting JWT cookies.
    unset_jwt_cookies(response):
        This method removes any access tokens from cookies if they were set using set_access_cookies.
    Clearing the refresh_token cookie:
        Sets the refresh_token cookie to an empty value with an expired timestamp, effectively removing it from the client.
    """
    response = jsonify({'message': 'Logged out successfully! 🌈'})
    unset_jwt_cookies(response)
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=True, samesite='Lax')
    return response


@auth.route('/register', methods=['POST'])
def register():
    """
    This function allows new poets to register by validating their details 
    (like email and password) and storing them in the database after hashing the password.
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
    hashed_password = generate_password_hash(poet_create.password_hash)

    # Step 3: Create new poet and save to the database
    new_poet = Poet(
            poet_name=poet_create.poet_name,
            email=poet_create.email,
            password_hash=hashed_password
        )
    db.session.add(new_poet)

    try:
        db.session.commit()
        db.session.refresh(new_poet)
        print('Poet(esse) registered and committed to the database. 🍰')  # Debug statement
        # Use PoetResponse Pydantic model to structure the response
        poet_response = PoetResponse.model_validate(new_poet)
        return jsonify(poet_response.model_dump()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error during registration commit: {e}. 🥒")  # Debug statement
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
