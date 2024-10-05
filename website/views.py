from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from .models import Poem, Poet
from .database import db
from .schemas import PoemCreate, PoemResponse


views = Blueprint('views', __name__)

@views.route('/home', methods=['GET', 'POST'])
@jwt_required()
def profile():
    pass


@views.route('/create-poem', methods=['POST'])
@jwt_required()
def create_poem():
    # Get current logged-in user ID from JWT token
    poet_id = get_jwt_identity()

    try:
        # Validate incoming JSON data using PoemCreate Pydantic model
        poem_data = PoemCreate(**request.json)

        # Create and save the poem to the database
        new_poem = Poem(
            title=poem_data.title,
            poem_type_id=poem_data.poem_type_id,
            is_collaborative=poem_data.is_collaborative,
            poet_id=poet_id  # Associate the poem with the currently logged-in poet
        )
        db.session.add(new_poem)
        db.session.commit()

        flash('Poem created successfully! 🦓', category='success')
        return redirect(url_for('views.home'))

    except ValidationError as e:
        flash('There was an error with your poem submission. 🌊 Please try again.', category='success')
