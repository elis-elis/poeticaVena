"""
The poem_val.py file handles the validation logic for different poem types.
"""

from flask import jsonify
from backend.poem_utils import get_last_contribution
import logging

def validate_poem_content(poem_type, current_poem_content, previous_lines):
    """
    Route to the correct poem content validation based on poem type.
    """
    from .haiku import validate_haiku
    from .free_verse import validate_free_verse
    from .nonet import validate_nonet

    if poem_type.name == 'Haiku':
        return validate_haiku(current_poem_content, previous_lines)
    elif poem_type.name == 'Nonet':
        return validate_nonet(current_poem_content, previous_lines)
    elif poem_type.name == 'Free Verse':
        return validate_free_verse(current_poem_content)
    # Add other poem types here as needed
    return None  # No validation needed for certain types


def validate_max_lines(poem_type, existing_contributions):
    """
    Validate the maximum lines allowed for the poem type.
    If adding another line would surpass the poem’s line limit, it stops the process and returns an error.
    """
    max_allowed_lines = poem_type.criteria.get('max_lines', None)
    # Check if max lines is defined in criteria
    if max_allowed_lines is None:
        return jsonify({'error': 'Poem type criteria missing max_lines definition. ⚡️'}), 500
    
    # Check if adding another line would exceed max lines
    if len(existing_contributions) + 1 > max_allowed_lines:
        return jsonify({'error': f'This poem has already reached the maximum number of {max_allowed_lines} lines. 🌿'}), 400

    # Return as a tuple: the max allowed lines and a status code 200
    return {'max_allowed_lines': max_allowed_lines}, 200


def validate_consecutive_contributions(existing_contributions, poet_id, poem_id):
    """
    Validates that the same poet cannot make two consecutive contributions to the same poem.
    """
    if not existing_contributions:
        return None

    last_contribution = get_last_contribution(poem_id)

    # Check if the last contribution was made by the same poet
    if last_contribution and last_contribution.poet_id == poet_id:
        return jsonify({'error': 'You cannot contribute twice in a row to the same poem. 🌵'}), 400

    return None
    