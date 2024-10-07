from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from .models import Poem, Poet
from .database import db
from .schemas import *


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@jwt_required()
def home():
    """
    This function serves as an entry point for authenticated users.
    """
    pass


@views.route('/poem-types', methods=['GET'])
def get_poem_types():
    """
    Fetch all available poem types and return them as JSON.
    """
    poem_types = Poem.query.all()   # The result is a list of PoemType objects

    # poem_types_response = [PoemTypeResponse.model_validate(poem_type) for poem_type in poem_types]
    poem_types_response = []
    for poem_type in poem_types:
        poem_type_response = PoemTypeResponse.model_validate(poem_type)
        poem_types_response.append(poem_type_response)
    
    return jsonify(poem_types_response), 200


@views.route('/create-poem', methods=['POST'])
@jwt_required()
def create_poem():
    """
    This function handles the submission of new poems:
        It retrieves the currently logged-in user's ID.
        It validates the poem data using the PoemCreate Pydantic model.
        If validation passes, it creates a new Poem entry in the database.
        It provides user feedback using the flash() method and redirects the user to the poem detail page.
    """
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
        return redirect(url_for('poem_detail', poem_id=new_poem.id))
        # for example, if the poem_detail route is something like /poems/<poem_id>, 
        # the user will be redirected to /poems/1 if the new poem’s ID is 1.

    except ValidationError as e:
        flash('There was an error with your poem submission. 🌊 Please try again.', category='success')
        return redirect(url_for('create_poem_form'))
        # For example, if the route for creating a new poem is /poems/new, 
        # this redirection will send the user back to /poems/new.
