from flask import jsonify
from .syllable_validator import validate_syllables

def validate_nonet(current_poem_content, existing_lines):
    expected_structure = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    return validate_syllables(current_poem_content, existing_lines, expected_structure)
