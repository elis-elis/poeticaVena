from flask import jsonify
from .database import db
from .models import Poem, PoemType, PoemDetails
from .schemas import PoemDetailsResponse
from .ai_val import check_ai_validation


def is_authorized_poet(requested_poet_id, authenticated_poet_id):
    """
    Check if the poet is authorized to submit the content.
    """
    return requested_poet_id == authenticated_poet_id


def get_poem_by_id(poem_id):
    """
    Fetch a poem by its ID from the database.
    """
    return Poem.query.get(poem_id)


def get_poem_type_by_id(poem_type_id):
    """
    Fetch a poem type by its ID from the database.
    """
    return PoemType.query.get(poem_type_id)


def get_poem_contributions(poem_id):
    """
    Count how many contributions exist for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).count()


def get_last_contribution(poem_id):
    """
    Fetch the most recent contribution to a collaborative poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.desc()).first()


def save_poem_details(poem_details_data):
    """
    Create and save PoemDetails entry in the database.
    """
    poem_details = PoemDetails(
        poem_id=poem_details_data.poem_id,
        poet_id=poem_details_data.poet_id,
        content=poem_details_data.content
    )

    db.seesio.add(poem_details)
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
    poem_type = get_poem_type_by_id(poem.poem_type_id)
    if not poem_type:
        return jsonify({'error': 'Poem type was not found. ⚡️'}), 404

    # Check existing contributions
    existing_contributions = get_poem_contributions(poem.id)
    if existing_contributions == 0:
        print(f'First contribution to collaborative poem by poet(esse) ID {poet_id}.')
    else:
        last_contribution = get_last_contribution(poem.id)
        if last_contribution.poet_id == poet_id:
            return jsonify({'error': 'You cannot contribute consecutive lines. 🦖'}), 400

    # AI validation (skipped for now)
    content_valid = True  # You can replace this with your AI validation logic.
    
    if not content_valid:
        return jsonify({'error': 'Contribution didn\'t pass AI validation. 🌦'}), 400
    
    # Publish the contribution
    poem_details = save_poem_details(poem_details_data)
    if check_if_collaborative_poem_completed(existing_contributions):
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Poem is now completed and published. 🌵'}), 201

    # Return the new poem details response
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify(poem_details_response.model_dump()), 201
