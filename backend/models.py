from .database import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Poet(db.Model, UserMixin):
    __tablename__ = 'poets'

    id = db.Column(db.Integer, primary_key=True)
    poet_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(260), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    # One-to-many relationship with Poem
    poems = db.relationship('Poem', backref='poet', lazy=True, passive_deletes=True)


class Poem(db.Model):
    __tablename__ = 'poems'

    id = db.Column(db.Integer, primary_key=True)
    poet_id = db.Column(db.Integer, db.ForeignKey('poets.id'), nullable=False)
    poem_type_id = db.Column(db.Integer, db.ForeignKey('poem_types.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_collaborative = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    # One-to-one or one-to-many relationship with PoemDetails
    poem_details = db.relationship('PoemDetails', backref='poem', lazy=True, passive_deletes=True)


class PoemType(db.Model):
    __tablename__ = 'poem_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.JSON, nullable=False)
    # One-to-many relationship with Poem
    poem = db.relationship('Poem', backref='poem_type', lazy=True)

class PoemDetails(db.Model):
    # Handles contributions, from a single poet or multiple poets for collaborative poems. 
    # It holds the poem's content and tracks when it was submitted.
    __tablename__ = 'poem_details'

    id = db.Column(db.Integer, primary_key=True)
    poem_id = db.Column(db.Integer, db.ForeignKey('poems.id'), nullable=False)
    poet_id = db.Column(db.Integer, db.ForeignKey('poets.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime(timezone=True), default=func.now())
