from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .schemas import PoetCreate, PoetResponse
from .models import Poet
from pydantic import ValidationError



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return '🪭 blind spots in the eyes'
    # return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Handle GET request (render the registration form)
    if request.method == 'GET':
        return render_template('register.html')

    # Handle POST request (user submits the registration form)
    if request.method == 'POST':
        # Retrieve form data
        poet_name=request.form.get('poet_name')
        email=request.form.get('email')
        password=request.form.get('password')
                
        
        # Step 1: Validation (basic validation checks)
        existing_poet = Poet.query.filter_by(email=email).first()
        if existing_poet:
            flash('Email already exists', category='info')
            return redirect(url_for('auth.register'))

        if len(poet_name) < 2:
            flash('Poet name must be at least two characters.', category='info')
            return redirect(url_for('auth.register'))
        
        if len(password) < 7:
            flash('Password must be at least seven characters.', category='info')
            return redirect(url_for('auth.register'))
            
        # Step 2: Hash the password
        hashed_password = generate_password_hash(password)

        # Step 3: Create new poet and save to the database
        new_poet = Poet(
                poet_name=poet_name,
                email=email,
                password_hash=hashed_password
            )
        db.session.add(new_poet)

        try:
            db.session.commit()
            flash('Account created successfully!', category='success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            if request.form:
                flash('An error occurred during registration. Please try again.', category='error')
                return redirect(url_for('auth.register'))
