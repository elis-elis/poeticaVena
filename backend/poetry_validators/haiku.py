from flask import jsonify
from .syllable_validator import validate_syllables


def validate_haiku(current_poem_content, existing_lines):
    """
    Validate Haiku's syllable structure: 5-7-5
    """
    expected_structure = [5, 7, 5]
    return validate_syllables(current_poem_content, existing_lines, expected_structure)
