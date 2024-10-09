from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from .models import Poem, PoemType, Poet, PoemDetails
from .database import db
from .schemas import PoemCreate, PoemTypeResponse, PoemResponse, PoemDetailsCreate, PoemDetailsResponse


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
    This function handles the submission of new poems:
        - Retrieves the currently logged-in user's ID.
        - Validates the poem data using the PoemCreate Pydantic model.
        - Creates a new Poem entry in the database if validation passes.
        - Returns a JSON response with the poem details or error message.
    """
    # Get current logged-in user (poet) ID from JWT token
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
        db.session.refresh(new_poem)


        # Manually print the new_poem fields
        print("New Poem created:", new_poem.id, new_poem.title, new_poem.created_at)

        # Use PoemResponse Pydantic model to return the poem data
        poem_response = PoemResponse.model_validate(new_poem)

        # Print the validated Pydantic model
        print("Pydantic Model:", poem_response)

        return jsonify(poem_response.model_dump()), 201

    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    

@routes.route('/submit-poem-details', methods=['POST'])
@jwt_required()
def submit_poem_details():
    """
    This route handles the submission of poem details (actual poetry content).
    It supports both individual and collaborative poem submissions.
    Collaborative poems are built line-by-line, validated by AI, and completed
    once all contributions pass the poem type's criteria.
    """
    poet_id =  get_jwt_identity()

    try:
        # Validate incoming data using PoemDetailsCreate Pydantic model
        poem_details_data = PoemDetailsCreate(**request.json)
        
        # This prevents poets from submitting content for poems they don’t own, adding an extra layer of security
        if poem_details_data.poet_id != poet_id:
            return jsonify({'error': 'You are not authorized to submit content for this poem. 🍳'}), 403
        
        # Check if the poem exists and whether it is collaborative or not
        poem = Poem.query.get(poem_details_data.poem_id)

        if not poem:
            return jsonify({'error': 'Poem was not found.'}), 404
        
        # Collaborative poem logic
        if poem.is_collaborative:
            print(f'Collaborative poem: {poem.title}')
            
            # Get poem type to validate criteria
            poem_type = PoemType.query.get(poem.poem_type_id)
            if not poem_type:
                return jsonify({'error': 'Poem type was not found. ⚡️'}), 404
            
            # Check if this is the first contribution
            exisiting_contributions = PoemDetails.query.filter_by(poet_id=poem.id).count()

            if exisiting_contributions == 0:
                # First contribution, the poet is setting the first line
                print(f'First contribution to collaborative poem by poet {poet_id}.')
            else:
                # Check if the same poet is contributing again or if it is out of sequence
                last_contribution = PoemDetails.query.filter_by(poem_id=poem.id).order_by(PoemDetails.submitted_at.desc()).first()
                if last_contribution == poet_id:
                    return jsonify({'error': 'You cannot contribute consecutive lines.'}), 400
                
            # Send the content to the AI for validation (pseudo-code, integrate your AI logic here)
            content_valid = check_ai_validation(poem_details_data.content, poem_type.criteria)
            
            if not content_valid:
                return jsonify({'error': 'Contribution didn\'t pass AI validation. Please try again and good luck. 🌦'}), 400
            
            # Publish the line if it passes AI validation
            poem_details = PoemDetails(
                poem_id=poem_details_data.poem_id,
                poet_id=poem_details_data.poet_id,
                content=poem_details_data.content
            )

            db.seesio.add(poem_details)
            db.session.commit()
            db.session.refresh(poem_details)

            # Check if this is the last contribution for the poem
            max_lines = 5  # make this dynamic!
            if exisiting_contributions + 1 >= max_lines:
                poem.is_published = True
                db.session.commit()
                return jsonify({'message': 'Poem is now completed and published. Thank you for your contributions. 🌵'}), 201
            
            # Return the new PoemDetails as a response
            poem_details_response = PoemDetailsResponse.model_validate(poem_details)

            return jsonify(poem_details_response.model_dump()), 201
            
        # Individual poem logic
        else:
            # This line queries the database to count how many entries in the PoemDetails table already exist for the given poem.id
            exisiting_contributions = PoemDetails.query.filter_by(poet_id=poem.id).count()
            if exisiting_contributions > 0:
                return jsonify({'error': 'This poem is not collaborative and already has content. 🪐'}), 400
            
            # Create the PoemDetails entry for individual poem
            poem_details = PoemDetails(
                poem_id=poem_details_data.poem_id,
                poet_id=poem_details_data.poet_id,
                content=poem_details_data.content
            )

            db.seesio.add(poem_details)
            db.session.commit()
            db.session.refresh(poem_details)

            # Return the new PoemDetails as a response
            poem_details_response = PoemDetailsResponse.model_validate(poem_details)

            return jsonify(poem_details_response.model_dump()), 201
    
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500



def check_ai_validation(content: str, criteria: str) -> bool:
    pass
