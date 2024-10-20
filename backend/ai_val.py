"""
Handles AI-based validation logic (i.e., sending prompts to the OpenAI API).
"""

import os
from openai import OpenAI
import logging


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv
from .poem_utils import get_poem_type_by_id, count_syllables_in_line


load_dotenv()


def fetch_poem_validation_from_ai(poem_line, line_number, criteria, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on poem type criteria.
    It explicitly ensures validation is focused on a specific line number.
    """
    # Get the poem type with its criteria
    poem_type = get_poem_type_by_id(poem_type_id)
    if not poem_type:
        return "Error: Poem type not found."

    # Construct a prompt based on the poem type's criteria
    prompt = f"""
    You are an expert poetry validator. Given the following criteria: {criteria} for a haiku,
    and focusing specifically on line {line_number} of the poem:
    {poem_line}
    Please validate ONLY line {line_number} against the syllable structure.
    The first line must have 5 syllables, The second line must have 7 syllables, The third line must have 5 syllables.
    Syllables should be counted in British English.
    Respond with 'Pass' if this line follows the required syllable structure. 
    If it does not, respond with 'Fail' and a concise explanation, specifically noting which line failed and why.
    """

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        # Make the call to the GPT model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Log the response for debugging
        logging.debug(f"Full response: {response}")

        choices = response.choices
        if choices and len(choices) > 0:
            message = choices[0].message.content.strip()
            logging.debug(f"Validating line {line_number}: '{poem_line}' with criteria: {criteria}")
            return message
        else:
            logging.error("Error: 'choices' missing or empty in response.")
            return "Error: No choices in response."

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"


def fetch_poem_validation_with_nltk_fallback(poem_line, line_number, criteria, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation. If AI fails, fall back to NLTK syllable counting.
    """
    # AI Validation
    validation_result = fetch_poem_validation_from_ai(poem_line, line_number, criteria, poem_type_id)

    # If AI validation passes, return the result
    if "Pass" in validation_result:
        return validation_result

    # If AI validation fails, fallback to NLTK syllable counting
    logging.warning(f"AI validation failed for line {line_number}: {validation_result}")

    # Fallback: Use NLTK syllable counting to validate
    nltk_syllable_count = count_syllables_in_line(poem_line)
    expected_syllables = [5, 7, 5][line_number - 1]  # Get expected syllables based on line number

    # Compare NLTK result with expected syllable count for the current line
    if nltk_syllable_count == expected_syllables:
        logging.info(f"NLTK fallback passed for line {line_number}. Syllables matched the {expected_syllables}-syllable structure.")
        return "Pass"
    else:
        logging.error(f"NLTK fallback failed for line {line_number}: Expected {expected_syllables} syllables, got {nltk_syllable_count}.")
        return f"Fail - NLTK counted {nltk_syllable_count} syllables, expected {expected_syllables}."
    