from flask import jsonify
from poetry_validators.haiku import validate_haiku
from poetry_validators.nonet import validate_nonet
from poetry_validators.free_verse import validate_free_verse
from poem_utils import get_last_contribution



def validate_poem_content(poem_type, current_poem_content, previous_lines):
    """
    Validate the current contribution based on the poem type.
    :param poem_type: The type of poem (e.g., Haiku, Nonet, etc.).
    :param current_poem_content: The line being contributed by the poet.
    :param previous_lines: The previous contributions from other poets.
    :return: JSON response if there is a validation error, or None if validation passed.
    """
    if poem_type.name == 'Haiku':
        return validate_haiku(current_poem_content, previous_lines)
    elif poem_type.name == 'Nonet':
        return validate_nonet(current_poem_content, previous_lines)
    elif poem_type.name == 'Free Verse':
        return validate_free_verse()

    # Add other poem types here as needed
    return None


def validate_max_lines(poem_type, existing_contributions):
    """
    Validate the maximum lines allowed for the poem type.
    """
    max_lines = poem_type.criteria.get('max_lines', None)
    if max_lines is None:
        return jsonify({'error': 'Poem type criteria missing max_lines definition. ⚡️'}), 500
    
    if existing_contributions + 1 > max_lines:
        return jsonify({'error': f'This poem has already reached the maximum number of {max_lines} lines. 🌿'}), 400

    return max_lines


def validate_consecutive_contributions(existing_contributions, poet_id, poem_id):
    """
    Check if the last contribution was made by the same poet.
    """
    if existing_contributions > 0:
        last_contribution = get_last_contribution(poem_id)
        if last_contribution.poet_id == poet_id:
            return jsonify({'error': 'You cannot contribute consecutive lines. 🦖'}), 400
    return None