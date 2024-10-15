"""
This file handles the overall submission process for individual and collaborative poems.

"""

from flask import jsonify
from .database import db
from .models import PoemDetails
from .schemas import PoemDetailsResponse
from .poem_utils import get_poem_type_by_id, get_poem_contributions, get_last_contribution, fetch_all_poem_lines
from poetry_validators.poem_val import validate_max_lines, validate_consecutive_contributions, validate_poem_content
from poem_utils import prepare_full_poem



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

    # Step 4: Validate max lines
    # If the validation returns a tuple (i.e., error message), it returns the tuple and stops further processing.
    max_lines = validate_max_lines(poem_type, existing_contributions)
    if isinstance(max_lines, tuple):
        return max_lines
    
    # Step 5: Check for consecutive contributions by the same poet
    consecutive_error = validate_consecutive_contributions(existing_contributions, poet_id, poem.id)
    if consecutive_error:
        return consecutive_error
        
    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)
        
    # Step 6: Validate poem type criteria format
    criteria = poem_type.criteria   # criteria is a dictionary (e.g., syllable count, rhyme scheme)
    if not criteria or 'max_lines' not in criteria:
        return jsonify({'error': 'Poem type criteria missing or invalid. ⚡️'}), 500

    # Step 7: Validate the current contribution based on the poem type
    # validation_result = fetch_poem_validation(current_poem_content, criteria, poem.poem_type_id)
    # Only validate the new contribution (current_poem_content) but pass previous_lines for context
    validation_error = validate_poem_content(poem_type, current_poem_content, previous_lines)
    if validation_error:
        return validation_error
    
    # If the contribution (or the whole poem so far) doesn't pass AI validation, return an error
    # if 'Pass' not in validation_result:
        # return jsonify({'error': 'Contribution didn\'t pass AI validation. Try again, dear poet(esse). 🌦'}), 400
    
    # Step 8: Save the contribution (publish it) after passing validation
    poem_details = save_poem_details(poem_details_data)

    # Step 9: Prepare the full poem so far
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Step 10: Check if the poem is now complete (i.e., number of contributions matches max_lines in criteria)
    if check_if_collaborative_poem_completed(existing_contributions + 1, criteria['max_lines']):
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Poem is now completed and published. 🌵'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted and published! Waiting for more contributions to complete the poem. 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,  # Display the entire poem including the new contribution
        'next_step': f'{criteria["max_lines"] - (existing_contributions + 1)} line(s) left to complete the poem.'
    }), 201
