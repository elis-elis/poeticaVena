from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from .models import Poem, PoemType, Poet
from .database import db
from .schemas import (
    PoemCreate, 
    PoemTypeResponse, 
    PoemResponse, 
    PoemDetailsCreate, 
    PoemUpdate, 
    PoetResponse
)
from .submit_poem_details import (
    process_individual_poem, 
    process_collaborative_poem, 
    is_authorized_poet
)
from .poem_utils import get_poem_by_id
from .poet_utils import fetch_poet, get_all_poets_query, get_current_poet
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
    return jsonify(message=f'You are (almost) welcomed here, dear poet(esse) {poet.poet_name} with ID {poet.id}. 🍸'), 200


@routes.route('/poet/me', methods=['GET'])
@jwt_required()
def get_poet():
    """
    Retrieves the profile of the logged-in poet(esse).
    """
    current_poet = get_current_poet()
    print(f"DEBUG: Retrieved JWT Identity in /poet route -> {current_poet}")
    
    if not current_poet:
            return jsonify({'error': 'Poet not found'}), 404
    
    poet_response = PoetResponse.model_validate(current_poet)
    return jsonify(poet_response.model_dump(exclude={"password_hash"})), 200


@routes.route('/poet/<int:poet_id>', methods=['GET'])
@jwt_required()
def get_poet_by_id(poet_id):
    """
    Retrieves information of any specific poet(esse) by poet_id.
    """
    try:
        # Fetch the requested poet by ID
        poet = fetch_poet(poet_id)
        
        if not poet:
            return jsonify({'error': 'Poet not found'}), 404

        # Validate and return the poet data
        poet_response = PoetResponse.model_validate(poet)
        return jsonify(poet_response.model_dump(exclude={"password_hash"})), 200
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@routes.route('/poet/<identifier>', methods=['GET'])
@jwt_required()
def get_poet_by_identifier(identifier):
    """
    Retrieves information of a specific poet by poet_id or poet_name.
    """
    try:
        # Check if identifier is an integer
        if identifier.isdigit():
            # Fetch by ID
            poet = Poet.query.filter(Poet.id == int(identifier)).first()
        else:
            # Fetch by name (case-insensitive)
            poet = Poet.query.filter(Poet.poet_name.ilike(f"%{identifier}%")).first()

        if not poet:
            return jsonify({'error': 'Poet not found'}), 404

        # Validate and return the poet data
        poet_response = PoetResponse.model_validate(poet)
        return jsonify(poet_response.model_dump(exclude={"password_hash"})), 200

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500


@routes.route('/poets', methods=['GET'])
@jwt_required()
def get_poets():
    """
    Retrieves a list of poets registered on the website with pagination.
    to test it: http://127.0.0.1:5000/get-poets?page=1&per_page=5
    """
    try:
        # Get pagination parameters from the query string
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=8)

        # Fetch poets with pagination
        poets_query = get_all_poets_query()
        poets_paginated = poets_query.paginate(page=page, per_page=per_page, error_out=False)

        # Prepare poet responses using the PoetResponse model
        poet_responses = [
            PoetResponse.model_validate(poet).model_dump(exclude={"password_hash"})
            for poet in poets_paginated.items
        ]

        # Prepare pagination metadata
        response_data = {
            'total': poets_paginated.total,
            'page': poets_paginated.page,
            'per_page': poets_paginated.per_page,
            'total_pages': poets_paginated.pages,
            'poets': poet_responses
        }

        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Error fetching poets: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@routes.route('/poem/<int:poem_id>', methods=['GET'])
@jwt_required()
def get_poem_by_id(poem_id):
    """
    Retrieves a specific poem's details and all its contributions.
    """
    try:
        # Fetch the poem details by ID
        poem = get_poem_by_id(poem_id)
        if not poem:
            logging.error(f'Poem with ID {poem_id} not found. 🪰')
            return jsonify({'error': 'Poem not found. 🌛'}), 404

        # Validate and serialize poem information using PoemResponse schema
        poem_data = poem.to_dict()
        poem_response = PoemResponse.model_validate(poem_data)

        return jsonify(poem_response.model_dump()), 200

    except Exception as e:
        logging.error(f"Error fetching poem with ID {poem_id}: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@routes.route('/all-poems', methods=['GET'])
@jwt_required()
def get_poems_with_five_filters():
    is_collaborative = request.args.get('is_collaborative')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)
    poem_type_id = request.args.get('poem_type_id', type=int)
    poet_id = request.args.get('poet_id', type=int)
    title = request.args.get('title')

    try:
        query = db.session.query(Poem)
        # Apply filtering based on collaborative status
        if is_collaborative is not None and is_collaborative.lower() == 'true':
            # Show only active collaborative poems (not published yet)
            query = query.filter(Poem.is_collaborative == True, Poem.is_published == False)
        if poem_type_id:
            query = query.filter(Poem.poem_type_id == poem_type_id)
        if poet_id:
            query = query.filter(Poem.poet_id == poet_id)
        if title:
            query = query.filter(Poem.title.ilike(f"%{title}%"))
        else:
            # Show only published poems
            query = query.filter(Poem.is_published == True)

        # Paginate the results
        poems_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build response data for each poem, using the Poem model's `to_dict` method
        poems_response = [poem.to_dict() for poem in poems_paginated.items]

        # Prepare pagination metadata
        response_data = {
            'total': poems_paginated.total,
            'page': poems_paginated.page,
            'per_page': poems_paginated.per_page,
            'total_pages': poems_paginated.pages,
            'poems': poems_response
        }

        return jsonify(response_data), 200
    
    except Exception as e:
        logging.error(f"Error fetching paginated poems: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@routes.route('/poems', methods=['GET'])
@jwt_required()
def get_poems_with_two_filters():
    """
    This route retrieves poems with filters for collaborative status and publication status, with pagination.
    If is_collaborative=true, we show only collaborative poems that are not yet published.
    Otherwise, we show only published poems.
    page and per_page are handled by SQLAlchemy’s paginate method on the query object.
    Since Poem includes a relationship with PoemDetails, calling to_dict() on each Poem object will also serialize each poem’s details into the response. 
    The poem_dict['details'] in Poem.to_dict() uses PoemDetails.to_dict() to format each PoemDetails entry.
    This route returns a JSON response that includes paginated poem results with details,
    filtered according to the is_collaborative and is_published criteria.
    """
    # Fetch query parameters for filtering and pagination
    is_collaborative = request.args.get('is_collaborative')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    try:
        query = db.session.query(Poem)
        # Apply filtering based on collaborative status
        if is_collaborative is not None and is_collaborative.lower() == 'true':
            # Show only active collaborative poems (not published yet)
            query = query.filter(Poem.is_collaborative == True, Poem.is_published == False)

        else:
            # Show only published poems
            query = query.filter(Poem.is_published == True)

        # Paginate the results
        poems_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build response data for each poem, using the Poem model's `to_dict` method
        poems_response = [poem.to_dict() for poem in poems_paginated.items]

        # Prepare pagination metadata
        response_data = {
            'total': poems_paginated.total,
            'page': poems_paginated.page,
            'per_page': poems_paginated.per_page,
            'total_pages': poems_paginated.pages,
            'poems': poems_response
        }

        return jsonify(response_data), 200
    
    except Exception as e:
        logging.error(f"Error fetching paginated poems: {str(e)}")
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


@routes.route('/submit-poem2', methods=['POST'])
@jwt_required()
def submit_poem2():
    try:
        # Find the poet by their email (whoch is stored in the token)
        poet = get_current_poet()
        if not poet:
            return jsonify({'error': 'Poet(esse) not found. 🦞'}), 404

        # Validate incoming JSON data using PoemCreate Pydantic model
        poem_data = PoemCreate(**request.json)

        existing_poem = db.session.query(Poem).filter_by(title=poem_data.title, poet_id=poet.id).first()
        if existing_poem:
            return jsonify({
                'error': 'Ah! 🍒 You already have a poem with this title. Please choose a different one.'
            }), 400

        # Create and save the poem to the database
        new_poem = Poem(
            title=poem_data.title,
            poem_type_id=poem_data.poem_type_id,
            is_collaborative=poem_data.is_collaborative,
            poet_id=poet.id,  # Associate the poem with the currently logged-in poet
            is_published=False  # Always set is_published to False on creation
        )

        db.session.add(new_poem)
        db.session.commit()
        db.session.refresh(new_poem)

        # Manually print the new_poem fields
        print("New Poem created:", new_poem.id, new_poem.title, new_poem.created_at)

        # Use PoemResponse Pydantic model to return the poem data
        poem_response = PoemResponse.model_validate(new_poem)

        return jsonify(poem_response.model_dump()), 201

    except JWTDecodeError:
        return jsonify({'error': 'Invalid token. Please log in again. ☔️'}), 401

    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'You already have a poem with this title. Please choose a different one.'
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


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
            return jsonify({'error': 'Poet(esse) not found. 🦞'}), 404

        # Validate incoming JSON data using PoemCreate Pydantic model
        poem_data = PoemCreate(**request.json)

        # Set `is_published` based on whether the poem is collaborative
        is_published = not poem_data.is_collaborative

        existing_poem = db.session.query(Poem).filter_by(title=poem_data.title, poet_id=poet.id).first()
        if existing_poem:
            return jsonify({
                'error': 'Ah! 🍒 You already have a poem with this title. Please choose a different one.'
            }), 400

        # Create and save the poem to the database
        new_poem = Poem(
            title=poem_data.title,
            poem_type_id=poem_data.poem_type_id,
            is_collaborative=poem_data.is_collaborative,
            poet_id=poet.id,  # Associate the poem with the currently logged-in poet
            is_published=is_published  # Publish only if the poem is individual
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
        return jsonify({'error': 'Invalid token. Please log in again. ☔️'}), 401

    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'You already have a poem with this title. Please choose a different one.'
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@routes.route('/submit-individual-poem', methods=['POST'])
@jwt_required()
def submit_individual_poem():
    """
    This route handles the full submission of a single, complete poem by one poet.
    """
    jwt_identity = get_jwt_identity()
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


@routes.route('/submit-collab-poem', methods=['POST'])
@jwt_required()
def submit_collaborative_contribution():
    """
    This route handles the contribution of lines to a collaborative poem, 
    with validation for contribution rules and poem progression.
    """
    jwt_identity = get_jwt_identity()

    # Extract poet_id from the identity stored in the JWT token
    poet_id = jwt_identity.get('poet_id')
    if not poet_id:
        return jsonify({'error': 'Invalid token data. Please log in again. 🍄'}), 401

    try:
        # Validate the incoming data using the PoemDetailsCreate schema
        poem_details_data = PoemDetailsCreate(**request.json)

        poem = get_poem_by_id(poem_details_data.poem_id)

        if not poem:
            logging.error('Poem not found when fetching by ID.')
            return jsonify({'error': 'Poem not found. ✨'}), 404

        # Authorization: Ensure the user is allowed to submit content for this poem
        if not is_authorized_poet(poem, poet_id):
            return jsonify({
                'error': 'Unfortunately (or fortunately) you are not authorized to submit content for this poem. 🍳'
            }), 403
        
        # If the poem is collaborative, proceed to process the contribution
        if poem.is_collaborative:
            return process_collaborative_poem(poem, poem_details_data, poet_id)
        else:
            return jsonify({'error': 'This is not a collaborative poem. 🐋'}), 400

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


@routes.route('/edit-poem/<int:poem_id>', methods=['GET', 'PATCH'])
@jwt_required()
def edit_poem(poem_id):
    """
    This route allows:
    - GET: Fetching the existing poem's metadata and content for editing.
    - POST: Editing and saving the poem's metadata and content.
    """
    try:
        poet = get_current_poet()
        if not poet:
            return jsonify({'error': 'Poet(esse) not found. 🏄‍♀️'}), 404

        # Fetch the poem by ID, ensuring it exists and is owned by the poet
        poem = get_poem_by_id(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found.'}), 404
        
        # Check if the poem is owned by the current poet (for individual poems)
        # OR if it's a collaborative poem, allow only editing specific contributions
        if poem.poet_id != poet.id and not poem.is_collaborative:
            return jsonify({
                'error': 'This is not your poem, therefore you do not have permission to edit this poem. 🍫'
            }), 403

        # Fetch poem details for display in edit form
        if request.method == 'GET':
            db.session.refresh(poem)

            poem_response = poem.to_dict()  # Convert the SQLAlchemy model to a dictionary
            print(f"DEBUG: Full poem dictionary: {poem_response}")
            # return jsonify(poem_response), 200
            poem_response = PoemResponse.model_validate(poem_response)
            return jsonify(poem_response.model_dump()), 200
    
        # Handle PUT request to update poem metadata and details
        elif request.method == 'PATCH':
            poem_update_data = PoemUpdate(**request.json)

            # Update poem fields if provided
            if poem_update_data.title is not None:
                poem.title = poem_update_data.title
            if poem_update_data.poem_type_id is not None:
                poem.poem_type_id = poem_update_data.poem_type_id
            poem.updated_at = datetime.now(timezone.utc)

            # Update existing PoemDetails entries
            if poem_update_data.details:
                # Map current poem details by ID for efficient updates
                existing_details = {detail.id: detail for detail in poem.poem_details}

                for details_data in poem_update_data.details:
                    if details_data.id and details_data.id in existing_details:
                        # Update content of each existing detail as provided
                        existing_detail = existing_details[details_data.id]

                        # Logic for Collaborative Poems
                        # Allow editing only if the current user is the contributor
                        if poem.is_collaborative and existing_detail.poet_id != poet.id:
                            continue    # Skip if the current user is not the contributor

                        # Update the content of each existing detail if the poet is authorized
                        existing_detail.content = details_data.content
                        existing_detail.submitted_at = datetime.now(timezone.utc)

            db.session.commit()
            db.session.refresh(poem)

            updated_poem_response = poem.to_dict()

            poem_response = PoemResponse.model_validate(updated_poem_response)
            return jsonify(poem_response.model_dump()), 200

    except ValidationError as e:
        logging.error(f"Validation error: {e.errors()}")
        return jsonify({'errors': e.errors()}), 400

    except Exception as e:
            logging.error(f"Error editing poem: {str(e)}")
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500 


@routes.route('/delete-poem/<int:poem_id>', methods=['DELETE'])
@jwt_required()
def delete_poem(poem_id):
    """
    Handles deletion of a poem by a specific poet.
    """
    try:
        poet = get_current_poet()
        if not poet:
            return jsonify({'error': 'Poet(esse) not found. 🏄‍♀️'}), 404
        
        poem = get_poem_by_id(poem_id)
        if not poem:
            return jsonify({'error': 'Poem not found. Maybe try again?'}), 404
        
        # Check if the poem is collaborative and deny deletion if it is
        if poem.is_collaborative:
            return jsonify({
                'error': 'Sorry, dear, but collaborative poems cannot be deleted by a single poet. 🐯'
            }), 403
        
        # Authorization check
        if poem.poet_id != poet.id:
            return jsonify({'error': 'oh, but you do not have permission to delete this poem. 🍽'}), 403

        # Delete the poem and commit changes
        db.session.delete(poem)
        db.session.commit()

        return jsonify({
            'status': 'success', 'message': 'Poem  deleted successfully. More room for new (sexy) poems. 🍇'
        }), 200

    except Exception as e:
        logging.error(f"Error deleting poem: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
