"""
This file handles the overall submission process for individual and collaborative poems.
"""

from flask import jsonify, request
from .database import db
from .models import PoemDetails
from .schemas import PoemDetailsResponse, PoemDetailsCreate
from .poem_utils import get_poem_type_by_id, get_poem_contributions
from backend.poetry_validators.free_verse import handle_free_verse
from backend.poetry_validators.haiku import handle_haiku
from backend.poetry_validators.nonet import handle_nonet
import logging


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

    print(f"Inside save_poem_details: {poem_details_data}, type: {type(poem_details_data)}")

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
    existing_contributions = get_poem_contributions(poem.id)
    current_poem_content = poem_details_data.content


    print(f"Delegating to handler for poem type: {poem_type.name}")

    # Delegate control to specific poem type handlers (Haiku, Free Verse, etc.)
    if poem_type.name == "Free Verse":
        return handle_free_verse(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    elif poem_type.name == "Haiku":
        return handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    elif poem_type.name == "Nonet":
        return handle_nonet(existing_contributions, current_poem_content, poem, poem_details_data, poet_id)
    
    return jsonify({'error': 'Poem type is not supported yet. 🌵'}), 400
