from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_nonet_validation_from_ai, fetch_poem_validation_from_nltk
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse
from backend.poetry_validators.poem_val import validate_consecutive_contributions



def validate_nonet_max_lines(existing_contributions):
    """
    Validate that Nonet can only have 9 lines.
    """
    max_allowed_lines = 9
    if existing_contributions + 1 > max_allowed_lines:
        return jsonify({'error': 'Nonet can only have 9 lines in total. 🌿'}), 400
    return None


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
    for i, line in enumerate(combined_lines):
        line_number = i + 1  # Line number in the poem (1-based index)
        expected_syllables = 9 - (i)  # 9 syllables for the first line, then decreasing by 1 for each subsequent line
        criteria = f"The current line should have {expected_syllables} syllables."

        # AI-based validation for Nonet structure
        validation_response = fetch_nonet_validation_from_ai(line, line_number, expected_syllables)
        
        # If AI validation fails, use NLTK as a fallback
        if "Fail" in validation_response:
            # Call the fallback function with NLTK syllable counting logic
            nltk_response = fetch_poem_validation_from_nltk(line, line_number, criteria, poem_type_id)

            # If NLTK also fails, return an error
            if "Fail" in nltk_response:
                return jsonify({'error': f'Line {line_number} failed validation. 🌦 Reason: {nltk_response}'}), 400

    # If all lines pass validation
    return None


def handle_nonet(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Nonet poems, ensuring the syllable structure is maintained.
    """
    from backend.submit_poem_details import save_poem_details
    
    previous_lines = fetch_all_poem_lines(poem.id)

    # Check for consecutive contributions
    consecutive_error = validate_consecutive_contributions(existing_contributions, poet_id, poem.id)
    if consecutive_error:
        return consecutive_error
    
    # Validate max lines for Haiku
    max_lines_error = validate_nonet_max_lines(existing_contributions)
    if max_lines_error:
        return max_lines_error

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
        return jsonify({'message': 'Nonet is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Continue contributing to complete the Nonet.' if existing_contributions + 1 < 9 else 'This Nonet is now complete and it reads good.'
    }), 201
