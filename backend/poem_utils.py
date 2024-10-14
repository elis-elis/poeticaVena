import re
from .models import Poem, PoemType, PoemDetails


def count_syllables(line):
    """Count the number of syllables in a given line of poetry."""
    line = line.lower()
    # Basic syllable counting using regex
    syllable_count = len(re.findall(r'[aeiouy]{1,2}', line))    # Count vowel clusters
    return syllable_count


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
    Count how many contributions exist for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).count() or 0


def get_last_contribution(poem_id):
    """
    Fetch the most recent contribution to a collaborative poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.desc()).first()


def fetch_all_poem_lines(poem_id):
    """
    Fetches and concatenates all existing lines for a collaborative poem.

    Args:
        poem_id: The ID of the poem for which to fetch lines.

    Returns:
        A string containing all the lines of the poem, concatenated with line breaks.
    """
    # Query the database for all poem details (lines) in the order they were submitted
    poem_lines = PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()

    # Extract the 'content' field from each PoemDetails record and join them with newlines
    all_lines = ""
    for detail in poem_lines:
        all_lines += detail.content + '\n'
        
    return all_lines
