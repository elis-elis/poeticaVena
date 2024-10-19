"""
This file handles the overall submission process for individual and collaborative poems.

"""

from flask import jsonify
from .database import db
from .models import PoemDetails
from .schemas import PoemDetailsResponse
from .poem_utils import get_poem_type_by_id, get_poem_contributions, get_last_contribution, fetch_all_poem_lines
from .poetry_validators.poem_val import validate_max_lines, validate_consecutive_contributions, validate_poem_content
from .poem_utils import prepare_full_poem



def is_authorized_poet(requested_poet_id, authenticated_poet_id):
    """
    Check if the poet is authorized to submit the content.
    """
    return requested_poet_id == authenticated_poet_id


def save_poem_details(poem_details_data):
    """
    Create and save PoemDetails entry in the database.
    """
    poem_details = PoemDetails(
        poem_id=poem_details_data.poem_id,
        poet_id=poem_details_data.poet_id,
        content=poem_details_data.content
    )

    db.session.add(poem_details)
    db.session.commit()
    db.session.refresh(poem_details)
    return poem_details


def check_if_collaborative_poem_completed(existing_contributions, max_lines):
    """
    Check if the collaborative poem is completed based on the number of contributions.
    """
    return existing_contributions + 1 >= max_lines


def process_individual_poem(poem, poem_details_data):
    """
    Handle logic for individual poem submissions.
    """
    exisiting_contributions = get_poem_contributions(poem.id)
    if exisiting_contributions > 0:
        return jsonify({'error': 'This poem is not collaborative and already has content. 🪐'}), 400
    
    poem_details = save_poem_details(poem_details_data)

    # Return the new PoemDetails as a response
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)

    return jsonify(poem_details_response.model_dump()), 201


def process_collaborative_poem(poem, poem_details_data, poet_id):
    """
    Handle logic for collaborative poem submissions.
    This function performs a series of validation steps before saving the poem.
        - Calls validate_max_lines() from poem_val.py.
        - Calls validate_consecutive_contributions() to ensure the same poet isn’t contributing consecutively.
        - Fetching the poem type criteria (e.g., max lines, rhyme scheme) from the database.
        The criteria must be present and valid; otherwise, the process stops.
        - Calls validate_poem_content() from poem_val.py.
        The previous lines are passed along with the current contribution for types 
        like Haiku and Nonet that require full-context validation.
    If all validation passes, the contribution is saved.
    It checks if the poem is complete and marks it as published if the maximum number of lines is reached.
    """
    # Step 1: Fetch and validate the poem type
    poem_type = get_poem_type_by_id(poem.poem_type_id)
    if not poem_type:
        return jsonify({'error': 'Poem type was not found. ⚡️'}), 404

    # Step 2: Check if the poem is already completed (published)
    if poem.is_published:
        return jsonify({'error': 'The poem is already completed and no more contributions can be made. 🌻'}), 400

    # Step 3: Fetch existing contributions
    existing_contributions = get_poem_contributions(poem.id)
    current_poem_content = poem_details_data.content

    # Step 4: Handle specific logic for different poem types
    if poem_type.name == "Free Verse":
        return handle_free_verse(existing_contributions, current_poem_content, poem, poem_details_data)
    elif poem_type.name == "Haiku":
        return handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    
    # Step 5: Common validation for all poem types (max lines, contributions, etc.)
    return validate_and_save_poem(poem_type, existing_contributions, current_poem_content, poem, poem_details_data, poet_id)


def validate_and_save_poem(poem_type, existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Common validation logic for all poem types, including max lines and contribution rules.
    """
    # Step 4: Validate max lines
    max_lines_error = validate_max_lines(poem_type, existing_contributions)
    if max_lines_error:
        return max_lines_error

    # Step 5: Check for consecutive contributions by the same poet
    consecutive_error = validate_consecutive_contributions(existing_contributions, poet_id, poem.id)
    if consecutive_error:
        return consecutive_error

    # Step 6: Validate the poem content based on poem type criteria
    previous_lines = fetch_all_poem_lines(poem.id)
    validation_error = validate_poem_content(poem_type, current_poem_content, previous_lines)
    if validation_error:
        return validation_error

    # Step 7: Save the contribution and prepare the full poem
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Step 8: Check if the poem is now complete (i.e., max lines reached)
    if check_if_collaborative_poem_completed(existing_contributions + 1, poem_type.criteria['max_lines']):
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Poem is now completed and published. 🌵'}), 201

    # Return poem details and next steps
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted and published! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': f'{poem_type.criteria["max_lines"] - (existing_contributions + 1)} line(s) left to complete the poem.'
    }), 201
