from flask import jsonify
from backend.poem_utils import count_syllables

def validate_haiku(current_poem_content, previous_lines):
    """
    Validate the current contribution for Haiku.
    Only the new line (current_poem_content) is validated, but previous lines provide context.
    """
    # Combine previous and current lines to get the full Haiku structure so far
    combined_lines = previous_lines.strip().split("\n") + [current_poem_content.strip()]
    
    # Haiku must have exactly 3 lines, but each poet adds one line at a time
    if len(combined_lines) > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400
    
    # Check if the current line violates the Haiku syllable structure
    syllable_counts = [count_syllables(line) for line in combined_lines]
    
    # For Haiku, check if syllable counts match the expected 5-7-5 structure
    expected_structure = [5, 7, 5]
    for i, syllables in enumerate(syllable_counts):
        if i < len(expected_structure) and syllables != expected_structure[i]:
            return jsonify({'error': f'Line {i+1} does not follow the required syllable count ({expected_structure[i]} syllables). 🌦'}), 400

    return None  # Validation passed
