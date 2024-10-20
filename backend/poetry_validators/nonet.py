from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_poem_validation_with_nltk_fallback
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse


def validate_nonet(current_poem_content, previous_lines, poem_type_id=2):
    """
    Validate the current contribution for Nonet using AI-based syllable validation with NLTK fallback.
    """
    # Combine previous lines with the new one
    combined_lines = [line for line in previous_lines.strip().split("\n") if line] + [current_poem_content.strip()]

    # Nonet must have exactly 9 lines
    if len(combined_lines) > 9:
        return jsonify({'error': 'Nonet can only have 9 lines in total. ⚡️'}), 400

    # The criteria for a Nonet poem is a syllable structure starting with 9 syllables and decreasing by 1 per line
    expected_syllables = 9 - (len(combined_lines) - 1)  # e.g., for the 1st line, expect 9 syllables, then 8, etc.
    criteria = f"The current line should have {expected_syllables} syllables."

    # Validate the latest line using AI + NLTK fallback
    line_number = len(combined_lines)
    validation_response = fetch_poem_validation_with_nltk_fallback(combined_lines[-1], line_number, criteria, poem_type_id)

    # If the AI or NLTK fallback returns "Fail", show the error
    if "Fail" in validation_response:
        return jsonify({'error': f'Line {line_number} failed validation. 🌦 Reason: {validation_response}'}), 400

    return None  # If validation passes


def handle_nonet(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Nonet poems, ensuring the syllable structure is maintained.
    """
    from backend.submit_poem_details import save_poem_details
    
    previous_lines = fetch_all_poem_lines(poem.id)

    print(f"Existing contributions: {existing_contributions}")
    print(f"Current poem state (is_published): {poem.is_published}")

    # Validate the Nonet structure (9 lines with decreasing syllables)
    poem_type_id = poem.poem_type_id  # Ensure the poem_type_id is being passed from the poem object
    validation_error = validate_nonet(current_poem_content, previous_lines, poem_type_id)
    if validation_error:
        return validation_error

    # Save the contribution after passing validation
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    # Check if the Nonet is now complete (9 lines in total)
    if existing_contributions + 1 == 9:
        poem.is_published = True
        db.session.commit()
        print(f"Nonet completed and published with 9 contributions.")
        return jsonify({'message': 'Nonet is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Continue contributing to complete the Nonet.' if existing_contributions + 1 < 9 else 'This Nonet is now complete.'
    }), 201
