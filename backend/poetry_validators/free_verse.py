from flask import jsonify
from backend.schemas import PoemDetailsResponse
from backend.poem_utils import prepare_full_poem


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
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    return jsonify({
        'message': 'Contribution accepted and published! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'continue writing until.... you die. 🦖'
    }), 201
