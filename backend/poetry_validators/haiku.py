from backend.database import db
from flask import jsonify
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse


def validate_haiku(current_poem_content, previous_lines):
    """
    Validate the current contribution for Haiku.
    Only the new line (current_poem_content) is validated, but previous lines provide context.
    """
    from backend.poem_utils import count_syllables_in_line

    # Combine previous and current lines to get the full Haiku structure so far
    # Filter out empty lines from previous_lines to avoid adding an empty line
    combined_lines = [line for line in previous_lines.strip().split("\n") if line] + [current_poem_content.strip()]

    # Print combined lines for debugging
    print(f"Combined lines: {combined_lines}")
    
    # Haiku must have exactly 3 lines, but each poet adds one line at a time
    if len(combined_lines) > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400
    
    # Check if the current line violates the Haiku syllable structure
    syllable_counts = [count_syllables_in_line(line) for line in combined_lines]

    # Print syllable counts for debugging
    print(f"Syllable counts: {syllable_counts}")
    
    # For Haiku, check if syllable counts match the expected 5-7-5 structure
    expected_structure = [5, 7, 5]
    for i, syllables in enumerate(syllable_counts):
        print(f"Line {i+1} syllables: {syllables}, expected: {expected_structure[i]}")
        if i < len(expected_structure) and syllables != expected_structure[i]:
            return jsonify({'error': f'Line {i+1} does not follow the required syllable count ({expected_structure[i]} syllables). 🌦'}), 400

    return None  # Validation passed


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems, ensuring the syllable structure is maintained.
    """
    from backend.submit_poem_details import save_poem_details

    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)

    # Validate the Haiku structure (5-7-5 syllables and 3 lines max)
    validation_error = validate_haiku(current_poem_content, previous_lines)
    if validation_error:
        return validation_error

    # Save the contribution after passing validation
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Check if the Haiku is now complete (3 lines in total)
    if len(previous_lines.split('\n')) + 1 == 3:
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Haiku is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Complete the Haiku with one more line.'
    }), 201
