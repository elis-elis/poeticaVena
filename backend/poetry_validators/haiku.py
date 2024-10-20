"""
Handles AI-based validation and manages the Haiku contribution logic.
"""

from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_poem_validation_from_ai
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse


def validate_haiku(current_poem_content, previous_lines, poem_type_id=1):
    """
    Validate the current contribution for Haiku using AI-based syllable validation.
    """
    # Combine previous and current lines to get the full Haiku structure so far
    # Filter out empty lines from previous_lines to avoid adding an empty line
    combined_lines = [line for line in previous_lines.strip().split("\n") if line] + [current_poem_content.strip()]

    # Print combined lines for debugging
    print(f"Combined lines: {combined_lines}")
    
    # Haiku must have exactly 3 lines, but each poet adds one line at a time
    if len(combined_lines) > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400
    
    # Create a prompt for the AI based on existing lines and the current poem
    criteria = "5-7-5 syllable structure"

    # Print syllable counts for debugging
    print(f"Syllable counts: {criteria}")
    
    # Validate each line
    for i, line in enumerate(combined_lines):
        ai_response = fetch_poem_validation_from_ai(line, criteria, poem_type_id)
        print(f"AI validation for line {i+1}: {ai_response}")  # Debugging purposes
        
        if "Fail" in ai_response:
            return jsonify({'error': f'Line {i+1} failed validation. 🌦 Reason: {ai_response}'}), 400

    return None  # If all lines pass validation


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems using AI validation.
    """
    from backend.submit_poem_details import save_poem_details

    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)

    # Log existing contributions and poem state
    print(f"Existing contributions: {existing_contributions}")
    print(f"Current poem state (is_published): {poem.is_published}")

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
        print(f"Haiku completed and published with 3 contributions.")
        return jsonify({'message': 'Haiku is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Complete the Haiku with one more line.' if existing_contributions + 1 < 3 else 'This Haiku is now complete.'
    }), 201
