from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from .models import Poem, PoemType
from .database import db
from .schemas import PoemCreate, PoemTypeResponse, PoemResponse, PoemDetailsCreate
from .submit_poem_details import process_individual_poem, process_collaborative_poem, is_authorized_poet
from .poem_utils import get_poem_by_id
import logging
from flask_jwt_extended.exceptions import JWTDecodeError


# Configure logging
logging.basicConfig(level=logging.ERROR)

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET'])
@jwt_required()
def home():
    """
    This function serves as an entry point for authenticated users.
    Currently returns a placeholder message for authenticated users.
    """
    poet_id = get_jwt_identity()    # Get the current user (poet) ID from the JWT token
    return jsonify(message=f'You are (almost) welcomed here, dear poet(esse) with ID {poet_id}. 🍸'), 200


@routes.route('/poem-types', methods=['GET'])
def get_poem_types():
    """
    Fetch all available poem types and return them as JSON.
    """
    poem_types = PoemType.query.all()   # The result is a list of PoemType objects

    # Validate each PoemType object using the PoemTypeResponse schema
    # poem_types_response = [PoemTypeResponse.model_validate(poem_type) for poem_type in poem_types]
    poem_types_response = []
    for poem_type in poem_types:
        poem_type_response = PoemTypeResponse.model_validate(poem_type)
        poem_types_response.append(poem_type_response)
    
    # Return the list of poem types as JSON
    return jsonify(poem_types_response), 200


@routes.route('/submit-poem', methods=['POST'])
@jwt_required()
def submit_poem():
    """
    This route handles the creation of a new poem. 
    It validates the input and saves the poem to the database. 
    This is typically where you’d create a poem before any lines are added.
        - Retrieves the currently logged-in user's ID.
        - Validates the poem data using the PoemCreate Pydantic model.
        - Creates a new Poem entry in the database if validation passes.
        - Returns a JSON response with the poem details or error message.
    """
    try:
        # Get current logged-in user (poet) ID from JWT token
        poet_id = get_jwt_identity()

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
        db.session.refresh(new_poem)


        # Manually print the new_poem fields
        print("New Poem created:", new_poem.id, new_poem.title, new_poem.created_at)

        # Use PoemResponse Pydantic model to return the poem data
        poem_response = PoemResponse.model_validate(new_poem)

        # Print the validated Pydantic model
        print("Pydantic Model:", poem_response)

        return jsonify(poem_response.model_dump()), 201

    except JWTDecodeError:
        return jsonify({'error': 'Invalid token. Please log in again.'}), 401

    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    

@routes.route('/submit-poem-details', methods=['POST'])
@jwt_required()
def submit_poem_details():
    """
    This route processes the content of a poem, which may involve either adding lines to an existing collaborative poem or handling individual poem submissions. 
    This is where you deal with the validation of lines and overall poem structure.
    """
    poet_id = get_jwt_identity()

    try:
        # Validate incoming data using PoemDetailsCreate Pydantic model
        poem_details_data = PoemDetailsCreate(**request.json)
        
        # Authorization check: ensure poet can submit content for this poem
        if not is_authorized_poet(poem_details_data.poet_id, poet_id):
            return jsonify({'error': 'You are not authorized to submit content for this poem. 🍳'}), 403
        
        # Check if the poem exists
        poem = get_poem_by_id(poem_details_data.poem_id)
        if not poem:
            return jsonify({'error': 'Poem was not found.'}), 404
        
        # Log the submission attempt
        logging.info(f"Poet {poet_id} is submitting content for poem {poem.id}.")

        # Process collaborative or individual poem logic
        if poem.is_collaborative:
            return process_collaborative_poem(poem, poem_details_data, poet_id)
        else:
            return process_individual_poem(poem, poem_details_data)
    
    except ValidationError as e:
        # Log validation errors
        logging.error(f"Validation error: {e.errors()}")
        return jsonify({'errors': e.errors()}), 400

    except Exception as e:
        logging.error(f"Error submitting poem: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
