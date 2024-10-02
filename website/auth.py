from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@auth.route('register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')



# Optional helper methods for password management
def set_password(self, password):
    self.password_hash = generate_password_hash(password, method='sha256')

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
    