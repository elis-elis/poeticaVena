from flask import jsonify
from backend.schemas import PoemDetailsResponse
from backend.poem_utils import prepare_full_poem
from backend.database import db


def validate_free_verse(current_poem_content):
    """
    Free verse poems do not have strict rules, 
    so this function can just return None.
    """
    return None


def handle_free_verse(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Free Verse poems, which have no specific structural validation.
    """
    from backend.submit_poem_details import save_poem_details

    poem_details = save_poem_details(poem_details_data)
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)

    # Prepare the full poem using the list of existing contributions
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    return jsonify({
        'message': 'Contribution accepted and published! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'continue writing until.... you die. 🦖'
    }), 201


def handle_free_verse_new(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    from backend.submit_poem_details import save_poem_details

    # Check if the poet wants to publish this Free Verse poem
    should_publish = poem_details_data.dict().get('publish', False)
    
    # Save the poem contribution details
    poem_details = save_poem_details(poem_details_data)
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)

    # Prepare the full poem with the latest contribution
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Publish the poem if the flag is set
    if should_publish:
        poem.is_published = True
        db.session.commit()

    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'is_published': poem.is_published,
        'next_step': 'Continue writing until you decide to publish , or until you decide to publish. 🦖'
    }), 201
