from backend.database import db
from flask import jsonify
from backend.ai_val import fetch_haiku_validation_from_ai, fetch_poem_validation_from_ai, fetch_poem_validation_from_nltk
from backend.models import PoemDetails
from backend.poem_utils import fetch_all_poem_lines, get_last_contribution, get_poem_by_id, get_poem_contributions, validate_line_syllables
from backend.poem_utils import prepare_full_poem
from backend.schemas import PoemDetailsResponse
from backend.poetry_validators.poem_val import validate_consecutive_contributions


def validate_haiku_max_lines(existing_contributions):
    """
    Validate that Haiku can only have 3 lines.
    """
    max_allowed_lines = 3
    if existing_contributions >= max_allowed_lines:
        return jsonify({'error': 'Haiku can only have 3 lines in total. 🌿'}), 400
    return None


def validate_haiku(current_poem_content, previous_lines):
    """
    Validate the current contribution for Haiku using AI-based syllable validation with NLTK fallback.
    """
    # exisiting_contributions = PoemDetails.query.filter_by(poem_id=poem_id).all()
    # Split the content into lines, including existing lines
    # Extract previous lines into a list, ensuring no empty lines
    previous_lines_list = [line for line in previous_lines.strip().split("\n") if line]
    combined_lines = previous_lines_list + [current_poem_content.strip()]

    # Debug: Confirm correct lines and count
    print(f"Combined lines (total {len(combined_lines)}): {combined_lines}")

    # Check for line count consistency with haiku requirements
    if len(combined_lines) > 3:
        return jsonify({'error': 'Haiku can only have 3 lines in total. ⚡️'}), 400

    # Calculate the line number for the current contribution
    current_line_number = len(previous_lines_list) + 1

    # Debug: Print details of the line being validated
    print(f"Validating line: '{current_poem_content}', line number: {current_line_number}")

    # Fetch AI validation for the current line only
    validation_response = fetch_haiku_validation_from_ai(current_poem_content, current_line_number)

    # Return an error if the validation fails
    if "Fail" in validation_response:
        return jsonify({'error': f'Line {current_line_number} failed validation. 🌦 Reason: {validation_response}'}), 400

    # If all validations pass, return None
    return None


def handle_haiku(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
    """
    Handle contributions for Haiku poems using AI validation.
    """
    from backend.submit_poem_details import save_poem_details

    # Combine all previous lines (for presentation purposes, not validation)
    # previous_lines = fetch_all_poem_lines(poem.id)

    # print(f"Previous lines fetched: {previous_lines}")

    # Check for consecutive contributions
    consecutive_error = validate_consecutive_contributions(existing_contributions, poet_id, poem.id)    # consecutive_error class tuple

    if consecutive_error:
        return consecutive_error
    
    # Validate max lines for Haiku
    max_lines_error = validate_haiku_max_lines(existing_contributions)
    if max_lines_error:
        return max_lines_error

    # Validate the poem using AI (this checks all lines so far)
    validation_error = validate_haiku_new(poem, current_poem_content)
    if validation_error:
        return validation_error

    # Save the contribution after passing AI validation
    poem_details = save_poem_details(poem_details_data)
    full_poem_so_far = prepare_full_poem(existing_contributions, current_poem_content, poem.id)

    print(f"existing_contributions: {existing_contributions}, type: {type(existing_contributions)}")
    print(f"full_poem_so_far: {full_poem_so_far}")

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
        'next_step': 'Complete the Haiku with one more line.' if existing_contributions + 1 < 3 else 'This Haiku is now complete and it reads good.'
    }), 201


def handle_haiku_old(existing_contributions, current_poem_content, poem, poem_details_data, poet_id):
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
