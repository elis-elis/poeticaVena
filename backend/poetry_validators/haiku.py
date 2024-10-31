import logging
from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_poem_validation_from_ai
from backend.models import PoemDetails
from backend.poem_utils import fetch_all_poem_lines, prepare_poem, validate_haiku_line
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse


def validate_haiku_line_with_fallback(line, line_num):
    """
    Attempts to validate a Haiku line using AI. If it fails, falls back to approximate syllable count.
    """
    # Step 1: Use AI to validate the line
    validation_response = fetch_poem_validation_from_ai(line, line_num, poem_type_id=1)

    # If AI validation fails, use the fallback syllable counter
    if "Fail" in validation_response:
        # Use the fallback syllable count validation
        fallback_response = validate_haiku_line(line, line_num)
        return fallback_response

    return validation_response


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems, ensuring the syllable structure is maintained.
    """
    from backend.submit_poem_details import save_poem_details
    
    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)

    # Check if previous_lines is a string to avoid errors when stripping or splitting
    if not isinstance(previous_lines, str):
        logging.error("Expected previous_lines to be a string but got a different type.")
        previous_lines = ""  # Fallback to empty string

    # Strip and split previous lines, ensuring to filter out empty strings
    previous_lines_list = [line for line in previous_lines.strip().split('\n') if line.strip()]

    # Existing contributions should be a list
    if not isinstance(existing_contributions, list):
        return jsonify({'error': 'Expected existing_contributions to be a list.'}), 400
    
    # Add current contribution
    combined_lines = previous_lines_list + [current_poem_content.strip()]
    line_number = len(combined_lines)

    # Debugging print
    print(f"Combined lines: {combined_lines}, Line Number: {line_number}")

    # Debug: Print details of the line being validated
    print(f"Previous lines: '{previous_lines}', line number: {line_number}")

    if line_number > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400

    # Validate the current line based on the line number
    validation_response = validate_haiku_line_with_fallback(current_poem_content, line_number)
    if "Fail" in validation_response:
        return jsonify({'error': f'Line {line_number} failed validation. 🌦 Reason: {validation_response}'}), 400

    # Save the contribution after passing validation
    poem_details = save_poem_details(poem_details_data)
    try:
        full_poem_so_far = prepare_poem(existing_contributions, current_poem_content, poem.id)
    except TypeError as e:
        logging.error(f"Error preparing full poem: {e}")
        return jsonify({'error': 'Error preparing the full poem content.'}), 500

    # Check if the Haiku is now complete (3 lines in total)
    if len(combined_lines) == 3:
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Haiku is now completed and published. 🌸', 'full_poem': full_poem_so_far}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Complete the Haiku with one more line.'
    }), 201
