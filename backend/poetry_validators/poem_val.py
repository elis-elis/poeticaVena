"""
The poem_val.py file handles the validation logic for different poem types.

"""

from flask import jsonify
from .haiku import validate_haiku
from .nonet import validate_nonet
from .free_verse import validate_free_verse
from backend.poem_utils import get_last_contribution



def validate_poem_content(poem_type, current_poem_content, previous_lines):
    """
    Validate the current contribution based on the poem type.
    """
    if poem_type.name == 'Haiku':
        return validate_haiku(current_poem_content, previous_lines)
    elif poem_type.name == 'Nonet':
        return validate_nonet(current_poem_content, previous_lines)
    elif poem_type.name == 'Free Verse':
        return validate_free_verse(current_poem_content)

    # Add other poem types here as needed

    return None


def validate_max_lines(poem_type, existing_contributions):
    """
    Validate the maximum lines allowed for the poem type.
    If adding another line would surpass the poem’s line limit, it stops the process and returns an error.
    """
    max_allowed_lines = poem_type.criteria.get('max_lines', None)
    if max_allowed_lines is None:
        return jsonify({'error': 'Poem type criteria missing max_lines definition. ⚡️'}), 500
    
    if existing_contributions + 1 > max_allowed_lines:
        return jsonify({'error': f'This poem has already reached the maximum number of {max_allowed_lines} lines. 🌿'}), 400

    return max_allowed_lines


def validate_consecutive_contributions(existing_contributions, poet_id, poem_id):
    """
    Check if the last contribution was made by the same poet.
    If the same poet tries to contribute twice in a row, it returns an error, stopping further processing.
    """
    if existing_contributions == 0:
        return None
    
    if existing_contributions > 0:
        last_contribution = get_last_contribution(poem_id)
        if last_contribution.poet_id == poet_id:
            return jsonify({'error': 'You cannot contribute consecutive lines. 🦖'}), 400
        
    return None