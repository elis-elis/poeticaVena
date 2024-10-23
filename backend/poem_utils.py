from .models import Poem, PoemType, PoemDetails
import nltk
from nltk.corpus import cmudict
import re

# Load the CMU Pronouncing Dictionary
nltk.download('cmudict')
d = cmudict.dict()


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
    Fetch all contributions for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).all() 

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


def prepare_full_poem(current_poem_content, poem_id):
    """
    Prepare the full poem so far including all previous contributions and the new one.
    This fetches the lines already contributed to the poem.
    The new line is concatenated with the existing content to form the complete poem preview.
    Use .strip() to remove any extra whitespace or newline characters. 
    Also, if previous_lines is empty (for new poems), the result is just the new content.
    """
    # Fetch the existing lines
    previous_lines = fetch_all_poem_lines(poem_id)
    
    # Combine the previous lines with the current contribution
    full_poem = f"{previous_lines.strip()}\n{current_poem_content.strip()}" if previous_lines else current_poem_content.strip()
    
    # Return the full poem so far
    return full_poem
