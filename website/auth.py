from flask import Blueprint, render_template, request, flash, redirect, url_for
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@auth.route('register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
