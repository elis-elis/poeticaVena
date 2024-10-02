from . import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Colum(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(260), nullable=False)
    poems = db._relationship('Poems', backref='author', lazy=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

class Poems(db.Model):
    __tablename__ = 'poems'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poem_type_id = db.Column(db.Integer, db.ForeignKey('poem_types.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_collaborative = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
