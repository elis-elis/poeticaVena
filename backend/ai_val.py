import os
from openai import OpenAI
import logging
from dotenv import load_dotenv
from .poem_utils import count_syllables_in_line

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_poem_validation_from_ai(poem_line, line_number, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on the specific poem type.
    It explicitly ensures validation is focused on a specific line number.
    """
    if poem_type_id == 1:
        return fetch_haiku_validation_from_ai(poem_line, line_number)
    elif poem_type_id == 2:
        return fetch_nonet_validation_from_ai(poem_line, line_number)
    else:
        return "Error: Poem type not recognized."


def fetch_haiku_validation_from_ai(poem_line, line_number):
    """
    Sends a Haiku poem line to OpenAI's API for validation based on the 5-7-5 syllable structure.
    """
    prompt = f"""
    You are an expert poetry validator. Given the Haiku structure (5-7-5 syllables), validate the following line.

    Poem line: "{poem_line}"
    Line number: {line_number}

    - First line: 5 syllables
    - Second line: 7 syllables
    - Third line: 5 syllables

    If the line follows this structure for the specified line number, respond with 'Pass'.
    If it does not, respond with 'Fail' and explain the discrepancy.
    """

    return make_ai_request(prompt)


def fetch_nonet_validation_from_ai(poem_line, line_number):
    """
    Sends a Nonet poem line to OpenAI's API for validation based on the 9-8-7-6-5-4-3-2-1 syllable structure.
    """
    expected_syllables = 9 - (line_number - 1)
    prompt = f"""
    You are an expert poetry validator. Given the Nonet structure, validate the following line.

    Poem line: "{poem_line}"
    Line number: {line_number}

    Expected syllables: {expected_syllables}

    If the line has the correct number of syllables, respond with 'Pass'.
    If it does not, respond with 'Fail' and explain the syllable count issue.
    """

    return make_ai_request(prompt)


def make_ai_request(prompt):
    """
    Helper function to handle sending the prompt to OpenAI and parsing the response.
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=100
        )

        choices = response.choices
        if choices and len(choices) > 0:
            return choices[0].message.content.strip()
        else:
            logging.error("Error: 'choices' missing or empty in response.")
            return "Error: No response from AI."
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"


def fetch_poem_validation_from_nltk(poem_line, line_number, criteria, poem_type_id):
    if poem_type_id == 1:
        return fetch_haiku_validation_with_nltk_fallback(poem_line, line_number, criteria)
    elif poem_type_id == 2:
        return fetch_nonet_validation_with_nltk_fallback(poem_line, line_number, criteria)
    else:
        return "Error: Poem type not recognized."


def fetch_haiku_validation_with_nltk_fallback(poem_line, line_number, criteria):
    # AI Validation
    validation_result = fetch_poem_validation_from_ai(poem_line, line_number, 1)

    if "Pass" in validation_result:
        return validation_result

    # Fallback to NLTK if AI validation fails
    nltk_syllable_count = count_syllables_in_line(poem_line)
    expected_syllables = [5, 7, 5][line_number - 1]

    return validate_nltk_syllables(nltk_syllable_count, expected_syllables)


def fetch_nonet_validation_with_nltk_fallback(poem_line, line_number, criteria):
    # AI Validation
    validation_result = fetch_poem_validation_from_ai(poem_line, line_number, 2)

    if "Pass" in validation_result:
        return validation_result

    # Fallback to NLTK if AI validation fails
    nltk_syllable_count = count_syllables_in_line(poem_line)
    expected_syllables = 9 - (line_number - 1)

    return validate_nltk_syllables(nltk_syllable_count, expected_syllables)


def validate_nltk_syllables(nltk_syllable_count, expected_syllables):
    if nltk_syllable_count == expected_syllables:
        return "Pass"
    else:
        return f"Fail - NLTK counted {nltk_syllable_count} syllables, expected {expected_syllables}."
