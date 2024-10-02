from . import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Colum(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(260), nullable=False)
    poems = db._relationship('Poems')
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())

class Poems(db.Model):
    id = db.Column(db.Integer, primary_key=True)


