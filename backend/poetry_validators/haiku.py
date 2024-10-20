"""
Handles AI-based validation and manages the Haiku contribution logic.
"""

from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_poem_validation_with_nltk_fallback
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse


def validate_haiku(current_poem_content, previous_lines, poem_type_id=1):
    """
    Validate the current contribution for Haiku using AI-based syllable validation with NLTK fallback.
    """
    # Combine previous and current lines to get the full Haiku structure so far
    # Filter out empty lines from previous_lines to avoid adding an empty line
    combined_lines = [line for line in previous_lines.strip().split("\n") if line] + [current_poem_content.strip()]

    # Print combined lines for debugging
    print(f"Combined lines: {combined_lines}")
    
    # Ensure the haiku has a maximum of 3 lines
    if len(combined_lines) > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400
    
    # Create a prompt for the AI based on existing lines and the current poem
    criteria = "5-7-5 syllable structure"
    
    # Validate the current line (we pass the line number and content)
    line_number = len(combined_lines)  # Current line number to be validated
    validation_response = fetch_poem_validation_with_nltk_fallback(combined_lines[-1], line_number, criteria, poem_type_id)
        
    if "Fail" in validation_response:
        return jsonify({'error': f'Line {line_number} failed validation. 🌦 Reason: {validation_response}'}), 400

    return None  # If all lines pass validation


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems using AI validation.
    """
    from backend.submit_poem_details import save_poem_details

    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)

    # Validate the poem using AI (this checks all lines so far)
    validation_error = validate_haiku(current_poem_content, previous_lines)
    if validation_error:
        return validation_error

    # Save the contribution after passing AI validation
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Check if the Haiku is complete (3 lines in total)
    if existing_contributions + 1 == 3:
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Haiku is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Complete the Haiku with one more line.' if existing_contributions + 1 < 3 else 'This Haiku is now complete.'
    }), 201
