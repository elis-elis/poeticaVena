from .models import Poem, PoemType, PoemDetails
# import re
from datetime import datetime, timedelta, timezone


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


def get_poem_contributions(poem_id):
    """
    Retrieve all contributions (lines) for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).all()


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
    Prepare the full poem so far including all previous contributions and the new one.
    """
    # Ensure existing_contributions is a list of lines
    if not isinstance(existing_contributions, list):
        raise ValueError(f"Unexpected type for existing_contributions: {type(existing_contributions)}")
    
    # Fetch all previous lines from the poem and split them into a list
    all_lines = fetch_all_poem_lines(poem_id).splitlines()

    # If the current content is not the last in existing_contributions, add it
    if not all_lines or all_lines[-1] != current_poem_content.strip():
        full_poem_lines = all_lines + [current_poem_content.strip()]
    else:
        full_poem_lines = all_lines

    # Join all lines with newlines to form the full poem text
    return "\n".join(full_poem_lines)


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
