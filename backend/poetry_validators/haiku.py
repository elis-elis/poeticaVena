from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_haiku_validation_from_ai, fetch_poem_validation_from_nltk
from backend.poem_utils import fetch_all_poem_lines
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse
from backend.poetry_validators.poem_val import validate_consecutive_contributions


def validate_haiku_max_lines(existing_contributions):
    """
    Validate that Haiku can only have 3 lines.
    """
    max_allowed_lines = 3
    if len(existing_contributions) >= max_allowed_lines:
        return jsonify({'error': 'Haiku can only have 3 lines in total. 🌿'}), 400
    return None


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
    
    # Validate each line based on its number and syllable structure (5-7-5)
    for i, line in enumerate(combined_lines):
        line_number = i + 1  # Line number to be validated (1-based index)

        # AI-based validation for Haiku (5-7-5 structure)
        validation_response = fetch_haiku_validation_from_ai(line, line_number)
        
        # If AI validation fails, use NLTK as a fallback
        if "Fail" in validation_response:
            # Call the fallback function with NLTK syllable counting logic
            nltk_response = fetch_poem_validation_from_nltk(line, line_number, "5-7-5 syllable structure", poem_type_id)

            # If NLTK also fails, return an error
            if "Fail" in nltk_response:
                return jsonify({'error': f'Line {line_number} failed validation. 🌦 Reason: {nltk_response}'}), 400

    # If all lines pass validation
    return None


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems using AI validation.
    """
    from backend.submit_poem_details import save_poem_details

    print('i am here')

    # Check for consecutive contributions
    consecutive_error = validate_consecutive_contributions(existing_contributions, poet_id, poem.id)
    
    if consecutive_error:
        return consecutive_error
    
    # Validate max lines for Haiku
    max_lines_error = validate_haiku_max_lines(existing_contributions)
    if max_lines_error:
        return max_lines_error

    # Combine all previous lines (for presentation purposes, not validation)
    previous_lines = fetch_all_poem_lines(poem.id)

    print(f"Previous lines fetched: {previous_lines}")


    # Validate the poem using AI (this checks all lines so far)
    validation_error = validate_haiku(current_poem_content, previous_lines)
    if validation_error:
        return validation_error

    # Save the contribution after passing AI validation
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)


    print(f"existing_contributions: {existing_contributions}, type: {type(existing_contributions)}")
    print(f"full_poem_so_far: {full_poem_so_far}")

    # Check if the Haiku is complete (3 lines in total)
    if len(existing_contributions) + 1 == 3:
        poem.is_published = True
        db.session.commit()
        return jsonify({'message': 'Haiku is now completed and published. 🌸'}), 201

    # Return the poem details along with the full poem so far
    poem_details_response = PoemDetailsResponse.model_validate(poem_details)
    return jsonify({
        'message': 'Contribution accepted! 🌱',
        'poem_details': poem_details_response.model_dump(),
        'full_poem': full_poem_so_far,
        'next_step': 'Complete the Haiku with one more line.' if len(existing_contributions) + 1 < 3 else 'This Haiku is now complete and it reads good.'
    }), 201
