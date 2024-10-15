from flask import jsonify
import json
from .database import db
from .models import PoemDetails
from .schemas import PoemDetailsResponse
from .poem_utils import get_poem_type_by_id, get_poem_contributions, get_last_contribution, fetch_all_poem_lines
from .ai_val import fetch_poem_validation



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
    Handle logic for collaborative poem submissions
    where each new contribution builds upon the previous lines.
    """
    # Step 1: Fetch and validate the poem type
    poem_type = get_poem_type_by_id(poem.poem_type_id)
    if not poem_type:
        return jsonify({'error': 'Poem type was not found. ⚡️'}), 404

    # Step 2: Fetch existing contributions
    existing_contributions = get_poem_contributions(poem.id)

    current_poem_content = poem_details_data.content

    # If no existing contributions, this is the first contribution
    if existing_contributions == 0:
        print(f'First contribution to collaborative poem by poet(esse) ID {poet_id}.')
    else:
        # Get the most recent contribution to check for consecutive contributions by the same poet
        last_contribution = get_last_contribution(poem.id)
        if last_contribution.poet_id == poet_id:
            return jsonify({'error': 'You cannot contribute consecutive lines. 🦖'}), 400
        
        # Combine all previous lines (for presentation purposes, not validation)
        previous_lines = fetch_all_poem_lines(poem.id)
        
    # Step 3: Validate poem type criteria format
    try:
        criteria = poem_type.criteria   # criteria is a dictionary (e.g., syllable count, rhyme scheme)
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Invalid poem criteria format: {str(e)}'}), 500

    # Step 4: Perform AI validation on the current line only
    validation_result = fetch_poem_validation(current_poem_content, criteria, poem.poem_type_id)
    
    # If the contribution (or the whole poem so far) doesn't pass AI validation, return an error
    if 'Pass' not in validation_result:
        return jsonify({'error': 'Contribution didn\'t pass AI validation. Try again. 🌦'}), 400
    
    # Step 5: Save the contribution (publish it) after passing validation
    poem_details = save_poem_details(poem_details_data)

    # Step 6: Prepare the full poem so far, including all previous contributions and the new one
    full_poem_so_far = previous_lines + "\n" + current_poem_content if existing_contributions > 0 else current_poem_content

    # Step 7: Check if the poem is now complete (i.e., number of contributions matches max_lines in criteria)
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
