from flask import jsonify
from .poem_utils import count_syllables


def validate_haiku(current_poem_content, existing_lines):
    """
    Validate Haiku's syllable structure: 5-7-5
    """
    # Split the content into lines, including existing lines
    lines = existing_lines.strip().split("\n") if existing_lines else []
    new_line = current_poem_content.strip()

    # Add the new line to the list of lines
    lines.append(new_line)

    # Check if the number of lines is appropriate
    if len(lines) > 3:
        return jsonify({'error': 'A Haiku must have exactly 3 lines.'}), 400

    # Check each line for syllable count
    syllable_counts = [count_syllables(line) for line in lines]

    # Check if syllable counts match Haiku structure: 5-7-5
    if len(lines) == 3 and syllable_counts != [5, 7, 5]:
        return jsonify({'error': 'Haiku does not follow the 5-7-5 syllable structure. 🌦'}), 400
    
    return None
