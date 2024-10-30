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


def get_poem_contributions_query(poet_id=None, days=None):
    """
    Constructs a query to retrieve poem contributions from the PoemDetails table or model in a database, 
    with optional filters for specific poets and recent submission dates.
    The function returns the query object itself.
    """
    query = PoemDetails.query

    if poet_id:
        query = query.filter(PoemDetails.poet_id == poet_id)

    if days:
        recent_date = datetime.now(timezone.utc) - timedelta(days=days)
        query = query.filter(PoemDetails.submitted_at >= recent_date)

    return query.order_by(PoemDetails.submitted_at.desc())


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
