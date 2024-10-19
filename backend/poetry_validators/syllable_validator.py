from flask import jsonify
from backend.poem_utils import count_syllables


def validate_syllables(current_poem_content, existing_lines, expected_structure):
    """
    Validate the syllable structure based on the expected syllable counts.
    """
    # Split the content into lines, including existing lines
    if existing_lines:
        # Remove any leading or trailing spaces or newlines, then split by newline
        existing_lines = existing_lines.strip()
        lines = existing_lines.split("\n")
    else:
        # If there are no existing lines, set `lines` to an empty list
        lines = []

    new_line = current_poem_content.strip()

    # Add the new line to the list of lines
    lines.append(new_line)

    # Check if the number of lines is appropriate
    if len(lines) > len(expected_structure):
        return jsonify({'error': f'This poem can have a maximum of {len(expected_structure)} lines.'}), 400

    # Check each line for syllable count
    syllable_counts = []  # Initialize an empty list to store the syllable counts for each line

    for line in lines:
        # Call the function `count_syllables()` for each line in the `lines` list
        syllable_count = count_syllables(line)
        
        # Append the syllable count to the `syllable_counts` list
        syllable_counts.append(syllable_count)

    # Compare with the expected structure
    if syllable_counts != expected_structure[:len(lines)]:
        return jsonify({'error': f'The syllable structure does not match the expected format. 🌦'}), 400
    
    return None
