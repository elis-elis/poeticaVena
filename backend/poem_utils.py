import re
from .models import Poem, PoemType, PoemDetails


def count_syllables(word):
    """
    Count the number of syllables in a word, handling common exceptions and
    applying standard syllable counting rules.
    """
    word = word.lower().strip()

    # Handle common exceptions (irregular syllable counts)
    exceptions = {
        'i': 1,
        'you': 1,
        'he': 1,
        'she': 1,
        'we': 1,
        'coffee': 2,
        'the': 1,
        'dropped': 1,
        'loved': 1
    }
    if word in exceptions:
        return exceptions[word]

    # If the word has fewer than 3 characters, it's likely one syllable
    if len(word) <= 3:
        return 1

    # Count the vowel groups in the word (a, e, i, o, u, and sometimes y)
    syllable_count = len(re.findall(r'[aeiouy]+', word))

    # Handle silent 'e' at the end of a word (but not "le")
    if word.endswith('e') and not word.endswith(('le', 'les')):
        syllable_count -= 1

    # Handle words ending in "le" preceded by a consonant (like "table")
    if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiou':
        syllable_count += 1

    # Ensure there is at least one syllable
    return max(1, syllable_count)


def count_syllables_in_line(line):
    """
    Count the syllables in a full line by splitting the line into words
    and summing their individual syllable counts.
    """
    # Split the line into words and count syllables per word
    words = re.findall(r'\b\w+\b', line.lower())
    syllable_count = sum(count_syllables(word) for word in words)
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


def prepare_full_poem(existing_contributions, current_poem_content, poem_id):
    """
    Prepare the full poem so far including all previous contributions and the new one.
    """
    if existing_contributions > 0:
        # Fetch and return all lines without appending the current content
        return fetch_all_poem_lines(poem_id)
    return current_poem_content
