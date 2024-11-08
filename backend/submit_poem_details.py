"""
This file handles the overall submission process for individual and collaborative poems.
"""

from flask import jsonify, request
from backend.poetry_validators.poem_val import validate_consecutive_contributions_new, validate_max_lines
from .database import db
from .models import PoemDetails
from .schemas import PoemDetailsResponse
from .poem_utils import get_poem_by_id, get_poem_type_by_id, get_poem_contributions
from backend.poetry_validators.free_verse import handle_free_verse
from backend.poetry_validators.haiku import handle_haiku
# from backend.poetry_validators.nonet import handle_nonet
# import logging


def is_authorized_poet(poem, authenticated_poet_id):
    """
    Check if the authenticated poet is authorized to submit the content.
    - For collaborative poems, allow any authenticated user to contribute.
    - For non-collaborative poems, only the original poet can contribute.
    """
    if poem.is_collaborative:
        # For collaborative poems, allow any authenticated user to submit content
        return True
    else:
        # For non-collaborative poems, only allow the original poet
        return poem.poet_id == authenticated_poet_id


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


def process_individual_poem(poem_details_data):
    """
    Handle logic for individual poem submissions.
    """
    # Check if the poem entry exists for this individual poem
    existing_poem = get_poem_by_id(poem_details_data.poem_id)
    if not existing_poem:
        return jsonify({'error': 'Poem does not exist. 🍅 or not found.'}), 404
    
    # Ensure the poem is marked as non-collaborative
    if existing_poem.is_collaborative:
        return jsonify({'error': 'This poem is collaborative and cannot be submitted as an individual poem. 🛼'}), 400

    # Save the individual poem content
    poem_details = PoemDetails(
        poem_id=poem_details_data.poem_id,
        poet_id=poem_details_data.poet_id,
        content=poem_details_data.content
    )
    db.session.add(poem_details)

    existing_poem.is_published = True

    db.session.commit()

    # Use PoemDetailsResponse to send back the details of the saved poem
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify(poem_details_response.model_dump()), 201


def process_collaborative_poem(poem, poem_details_data, poet_id):
    """
    Handle logic for collaborative poem submissions.
    """
    # Step 1: Fetch and validate the poem type
    poem_type = get_poem_type_by_id(poem.poem_type_id)
    print(f"Poem type retrieved: {poem_type.name if poem_type else 'None'}")

    if not poem_type:
        return jsonify({'error': 'Poem type was not found. ⚡️'}), 404

    print(f"Is the poem published? {'Yes' if poem.is_published else 'No'}")

    # Step 2: Check if the poem is already completed (published)
    if poem.is_published:
        return jsonify({'error': 'The poem is already completed and no more contributions can be made. 🌻'}), 400

    # Step 3: Fetch existing contributions
    existing_contributions_data = get_poem_contributions(poem.id)
    existing_contributions = [contribution.content for contribution in existing_contributions_data if contribution.content.strip()]  # Extract and filter out empty lines
    
    # Consecutive contributions validation
    consecutive_error = validate_consecutive_contributions_new(existing_contributions_data, poet_id, poem.id)
    if consecutive_error:
        return consecutive_error
    
    # Step 4: Validate max lines
    max_lines_validation, status_code = validate_max_lines(poem_type, existing_contributions)
    if status_code != 200:
        return max_lines_validation, status_code
    
    current_poem_content = poem_details_data.content

    print(f"Delegating to handler for poem type: {poem_type.name}")

    # Delegate control to specific poem type handlers (Haiku, Free Verse, etc.)
    if poem_type.name == "Free Verse":
        return handle_free_verse(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    elif poem_type.name == "Haiku":
        return handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    # elif poem_type.name == "Nonet":
        # return handle_nonet(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    
    return jsonify({'error': 'Poem type is not supported yet. 🌵'}), 400
