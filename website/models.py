from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Poet(db.Model, UserMixin):
    __tablename__ = 'poets'

    id = db.Column(db.Integer, primary_key=True)
    poet_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(260), nullable=False)
    poem = db.relationship('Poem', backref='poet', lazy=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

class Poem(db.Model):
    __tablename__ = 'poems'

    id = db.Column(db.Integer, primary_key=True)
    poet_id = db.Column(db.Integer, db.ForeignKey('poet.id'), nullable=False)
    poem_type_id = db.Column(db.Integer, db.ForeignKey('poem_type.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_collaborative = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

class PoemType(db.Model):
    __tablename__ = 'poem_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.Text, nullable=False)
    poem = db.relationship('Poem', backref='poem_type', lazy=True)

class PoemDetails(db.Model):
    __tablename__ = 'poem_details'

    id = db.Column(db.Integer, primary_key=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poem.id'), nullable=False)
    poet_id = db.Column(db.Integer, db.ForeignKey('poet.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime(timezone=True), default=func.now())
