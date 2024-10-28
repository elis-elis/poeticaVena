from .models import Poem, PoemType, PoemDetails
#import nltk
#from nltk.corpus import cmudict
import re

# Load the CMU Pronouncing Dictionary
# nltk.download('cmudict')
# d = cmudict.dict()


def validate_line_syllables(line, line_num):
    """
    Validates the syllable count in a line by counting vowel groups as syllables.
    """
    # Count syllables based on vowel groups in each word
    syllable_count = sum(len(re.findall(r'[aeiouy]+', word.lower())) for word in line.strip().split())

    # Check syllable count based on the line number in the Haiku
    if line_num == 1 and syllable_count == 5:
        return 'Pass'
    elif line_num == 2 and syllable_count == 7:
        return 'Pass'
    elif line_num == 3 and syllable_count == 5:
        return 'Pass'
    else:
        return f'Fail - The line has {syllable_count} syllables instead of the required {5 if line_num in [1, 3] else 7}.'
    

def nltk_syllable_count(word):
    """
    Uses the CMU Pronouncing Dictionary to count syllables in a word.
    If the word is not found, a regex-based estimate is returned.
    """
    word = word.lower()
    
    if word in d:
        # If the word is found, get syllable count from the first pronunciation in the dictionary
        return max([len([syl for syl in pronunciation if syl[-1].isdigit()]) for pronunciation in d[word]])
    else:
        # If word not found in CMU dictionary, fallback to rough syllable count using regex.
        # This counts vowels and assumes one vowel = one syllable.
        return len(re.findall(r'[aeiouy]+', word.lower()))
    

def count_syllables_in_line(line):
    """
    Count syllables in an entire line by splitting it into words and counting syllables in each word.
    """
    words = re.findall(r'\b\w+\b', line.lower())  # Extract words from the line
    syllable_count = sum(nltk_syllable_count(word) for word in words)

    print(f"Line: \"{line}\", Words: {words}, Total Syllables: {syllable_count}")

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


def fetch_all_poem_lines_other(poem_id):
    """
    Fetches and concatenates all existing lines for a collaborative poem.
    """
    # Query the database for all poem details (lines) in the order they were submitted
    return PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()


def fetch_all_poem_lines(poem_id):
    """
    Fetches and concatenates all existing lines for a collaborative poem, with each line on a new line.
    """
    # Query the database for all poem details (lines) in the order they were submitted
    poem_lines = PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.asc()).all()

    # Extract the 'content' field from each PoemDetails record and join them with newlines
    all_lines = "\n".join(detail.content for detail in poem_lines)

    return all_lines


def prepare_full_poem(existing_contributions, current_poem_content, poem_id):
    """
    Prepare the full poem so far including all previous contributions and the new one.
    """
    if isinstance(existing_contributions, int):
        if existing_contributions > 0:
            all_lines = fetch_all_poem_lines(poem_id)
            return ", ".join(all_lines + [current_poem_content.strip()])
        return current_poem_content.strip()
    else:
        raise ValueError(f"Unexpected type for existing_contributions: {type(existing_contributions)}")
