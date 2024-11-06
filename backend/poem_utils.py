import logging
from flask import jsonify
from .models import Poem, PoemType, PoemDetails
# import re
from datetime import datetime, timedelta, timezone
from .database import db
from sqlalchemy.orm import joinedload


def count_syllables(line):
    line = line.lower().strip()
    if line == "":
        return 0
    
    # Replace common silent letters
    line = line.replace("e ", " ")
    line = line.replace("e,", " ")
    line = line.replace("ed ", " ")
    line = line.replace("ed,", " ")

    vowels = "aeiouy"
    syllable_count = 0
    is_prev_char_vowel = False

    for char in line:
        if char in vowels:
            if not is_prev_char_vowel:
                syllable_count += 1
                is_prev_char_vowel = True
        else:
            is_prev_char_vowel = False

    # Handle special cases
    if line.endswith('e'):
        syllable_count -= 1

    # Ensure at least one syllable
    syllable_count = max(syllable_count, 1)

    return syllable_count


def validate_haiku_line(line, line_number):
    expected_syllables = [5, 7, 5]
    syllable_count = count_syllables(line)

    print(f"Validating line '{line}': Found {syllable_count} syllables (expected {expected_syllables[line_number - 1]})")

    if syllable_count == expected_syllables[line_number - 1]:
        return "Pass"
    else:
        return f'Fail: The line "{line}" has {syllable_count} syllables (expected {expected_syllables[line_number - 1]}).'


def get_poem_type_by_id(poem_type_id):
    """
    Fetch a poem type by its ID from the database.
    """
    return PoemType.query.get(poem_type_id)


def get_poem_by_id(poem_id):
    """
    Fetch a poem by its ID from the database.
    """
    return Poem.query.get(poem_id)


def get_full_poem_by_id(poem_id):
    """
    Fetch a Poem with its PoemDetails loaded.
    """
    return Poem.query.options(joinedload(Poem.poem_details)).filter_by(id=poem_id).first()


def get_poem_contributions(poem_id):
    """
    Retrieve all contributions (lines) for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).all()


def get_poem_contributions_query(poet_id=None, days=None):
    """
    Constructs a query to retrieve poem contributions from the PoemDetails table or model in a database, 
    with optional filters for specific poets and recent submission dates.
    The function returns the query object itself.
    """
    query = db.session.query(PoemDetails).join(Poem, PoemDetails.poem_id == Poem.id)

    if poet_id:
        query = query.filter(PoemDetails.poet_id == poet_id)

    if days:
        recent_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(PoemDetails.submitted_at >= recent_date)

    return query


def get_last_contribution(poem_id):
    """
    Fetch the most recent contribution to a collaborative poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.desc()).first()


def fetch_all_poem_lines(poem_id):
    """
    Fetches and concatenates all existing lines for a collaborative poem, with each line on a new line.
    """
    # Query the database for all poem details (lines) in the order they were submitted
    poem_lines = PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()

    # Extract the 'content' field from each PoemDetails record and join them with newlines
    all_lines = "\n".join(detail.content for detail in poem_lines)

    return all_lines


def fetch_all_poems_lines(poem_id, exclude_line=None):
    """
    Fetches and concatenates all existing lines for a collaborative poem, with each line on a new line,
    and excludes the specified `exclude_line`.
    """
    poem_lines = PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()

    # Extract the 'content' field from each PoemDetails record, excluding the last line if it matches exclude_line
    all_lines = [
        detail.content for detail in poem_lines
        if detail.content.strip() != (exclude_line.strip() if exclude_line else "")
    ]
    
    return "\n".join(all_lines)


def fetch_poem_lines(poem_id):
    """
    Fetches all existing contributions (lines) for a collaborative poem as individual records.
    """
    # Query the database for all poem details (lines) in the order they were submitted
    poem_lines = PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()

    # Return the list of PoemDetails records directly
    return poem_lines


def prepare_full_poem(existing_contributions, current_poem_content, poem_id):
    """
    Prepare the full poem so far, ensuring no duplicate contributions are appended.
    """
    # Ensure existing_contributions is a list of lines
    if not isinstance(existing_contributions, list):
        raise ValueError(f"Unexpected type for existing_contributions: {type(existing_contributions)}")
    
    # Fetch previous lines in correct order, excluding `current_poem_content` to avoid duplication
    all_lines = fetch_all_poems_lines(poem_id)

    # Append the current content as the last line
    full_poem_lines = all_lines + [current_poem_content.strip()]

    return full_poem_lines


def prepare_poem(existing_contributions, current_poem_content, poem_id):
    """
    Prepare the full poem content by combining existing contributions with the current content.
    """
    # Ensure existing_contributions is a list of strings, join if necessary
    if isinstance(existing_contributions, list):
        existing_contributions = "\n".join(existing_contributions)
    elif not isinstance(existing_contributions, str):
        logging.error("Expected existing_contributions to be a string or list of strings.")
        return jsonify({'error': 'Error: Contributions format is invalid.'}), 500

    # Ensure current_poem_content is a string
    if isinstance(current_poem_content, list):
        current_poem_content = " ".join(current_poem_content)
    elif not isinstance(current_poem_content, str):
        logging.error("Expected current_poem_content to be a string.")
        return jsonify({'error': 'Error: Current poem content format is invalid.'}), 500

    # Combine the existing contributions with the current line
    full_poem = f"{existing_contributions}\n{current_poem_content}".strip()
    
    return full_poem


def prepare_full_poems(poem_details):
    """
    Concatenates all content entries in PoemDetails to create the full poem text.
    """
    return "\n".join(detail.content for detail in poem_details)


def get_poem_contributions_paginated(page=1, per_page=10, poet_id=None, days=None):
    """
    Retrieves a paginated list of poem contributions from a database with 
    optional filters for a specific poet or a recent time range.
    The function returns paginated_contributions.items, which is a list of contributions for the specified page, 
    providing only the items that meet the filter criteria.
    """
    query = PoemDetails.query
    # Filter by poet_id if provided
    if poet_id:
        query = query.filter_by(poet_id=poet_id)
    # Filter by recent days if provided
    if days:
        # If days is provided, a recent date threshold is calculated by subtracting the days count from the current UTC date and time
        recent_date = datetime.now(timezone.utc) - timedelta(days=days)
        # The query is then filtered to only include contributions with a submitted_at timestamp that is later than or equal to this recent date threshold
        query = query.filter(PoemDetails.submitted_at >= recent_date)
    # Apply pagination
    paginated_contributions = query.order_by(PoemDetails.submitted_at.desc()).paginate(page=page, per_page=per_page)
    return paginated_contributions.tems   # Returns a list of contributions for the current page
