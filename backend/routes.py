from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from .models import Poem, PoemType, Poet
from .database import db
from .schemas import PoemCreate, PoemTypeResponse, PoemResponse, PoemDetailsCreate, PoetResponse
from .submit_poem_details import process_individual_poem, process_collaborative_poem, is_authorized_poet
from .poem_utils import get_poem_by_id
from .poet_utils import get_all_poets, get_current_poet
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
    poet = get_current_poet()
    return jsonify(message=f'You are (almost) welcomed here, dear poet(esse) with ID {poet}. 🍸'), 200


@routes.route('/get-poets', methods=['GET'])
@jwt_required()
def get_poets():
    """
    Retrieves a list of poets registered on the website.
    """
    try:
        poets = get_all_poets()

        # Create a response structure using PoetResponse schema
        poet_responses = [PoetResponse.model_validate(poet).model_dump() for poet in poets]

        return jsonify(poet_responses), 200
    
    except Exception as e:
        logging.error(f"Error fetching poets: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


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
        - Retrieves the currently logged-in user's email.
        - Validates the poem data using the PoemCreate Pydantic model.
        - Creates a new Poem entry in the database if validation passes.
        - Returns a JSON response with the poem details or error message.
    """
    try:
        # Find the poet by their email (whoch is stored in the token)
        poet = get_current_poet()
        if not poet:
            return jsonify({'error': 'Poet not found.'}), 404
        
        # Validate incoming JSON data using PoemCreate Pydantic model
        poem_data = PoemCreate(**request.json)

        print(poem_data)

        # Create and save the poem to the database
        new_poem = Poem(
            title=poem_data.title,
            poem_type_id=poem_data.poem_type_id,
            is_collaborative=poem_data.is_collaborative,
            poet_id=poet.id  # Associate the poem with the currently logged-in poet
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


@routes.route('/submit-individual-poem', methods=['POST'])
@jwt_required()
def submit_individual_poem():
    """
    This route handles the full submission of a single, complete poem by one poet.
    """
    jwt_identity = get_jwt_identity()  # Returns a dictionary with both poet_id and email

    # Extract poet_id and email from the identity stored in the JWT token
    poet_id = jwt_identity.get('poet_id')

    try:
        # Validate and create the individual poem
        poem_data = PoemDetailsCreate(**request.json)
        return process_individual_poem(poem_data)
    
    except ValidationError as e:
        logging.error(f"Validation Error: {e.errors()}")
        return jsonify({'status': 'error', 'message': 'Validation failed', 'errors': e.errors()}), 400
    
    #except SQLAlchemyError as db_error:
        #logging.error(f"Database error for poet {poet_id} with poem {poem_data.dict()}: {str(db_error)}")
        #db.session.rollback()
        #return jsonify({'status': 'error', 'message': 'A database error occurred.'}), 500
    
    except Exception as e:
        logging.error(f"Error submitting individual poem: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500


@routes.route('/submit-collab-contribution', methods=['POST'])
@jwt_required()
def submit_collaborative_contribution():
    """
    This route handles the contribution of lines to a collaborative poem, with validation for contribution rules and poem progression.
    """
    jwt_identity = get_jwt_identity()

    # Extract poet_id from the identity stored in the JWT token
    poet_id = jwt_identity.get('poet_id')
    if not poet_id:
        return jsonify({'error': 'Invalid token data. Please log in again.'}), 401

    try:
        # Validate the incoming data using the PoemDetailsCreate schema
        poem_details_data = PoemDetailsCreate(**request.json)

        poem = get_poem_by_id(poem_details_data.poem_id)

        if not poem:
            logging.error('Poem not found when fetching by ID.')
            return jsonify({'error': 'Poem not found.'}), 404

        # Authorization: Ensure the user is allowed to submit content for this poem
        if not is_authorized_poet(poem, poet_id):
            return jsonify({'error': 'You are not authorized to submit content for this poem. 🍳'}), 403
        
        # If the poem is collaborative, proceed to process the contribution
        if poem.is_collaborative:
            return process_collaborative_poem(poem, poem_details_data, poet_id)
        else:
            return jsonify({'error': 'This is not a collaborative poem.'}), 400

    except ValidationError as e:
        logging.error(f"Validation error: {e.errors()}")
        return jsonify({'errors': e.errors()}), 400
    
    except ValueError as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 404

    except Exception as e:
        logging.error(f"Error submitting collaborative contribution: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
