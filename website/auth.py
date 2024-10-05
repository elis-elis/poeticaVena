from flask import Blueprint, render_template, request, flash, redirect, url_for
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .models import Poet
from datetime import timedelta


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Poets can log in with their email and password. 
    If valid, they are logged in and redirected to the home page. 
    If not, appropriate error messages are shown.
    """
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

    # Find poet by email
    poet = Poet.query.filter_by(email=email).first()
    if poet:
        if check_password_hash(poet.password, password):
            flash('Logged in successfully! 🦩', category='success')
            # create a JWT access token
            access_token = create_access_token(identity=poet.id, expires_delta=timedelta(hours=1))
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect password. 🦄 Please try again.', category='error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth.route('/logout')
def logout():
    """
    Logs the user out and redirects them to the login page.
    """
    flash('Logged out successfully! 🌈', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    New poets can register for an account after passing several validation checks. 
    Their password is securely hashed, and their account is saved to the database. 
    If successful, they are redirected to the log-in page.
    """
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
            flash('Email already exists. 🥝', category='info')
            return redirect(url_for('auth.register'))

        if len(poet_name) < 2:
            flash('Poet name must be at least two characters. 🧃', category='info')
            return redirect(url_for('auth.register'))
        
        if len(password) < 7:
            flash('Password must be at least seven characters. 🪰', category='info')
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
            flash('Account created successfully! 👑', category='success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. 🪭 Please try again.', category='error')
            return redirect(url_for('auth.register'))
