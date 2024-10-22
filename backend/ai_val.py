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


def fetch_poem_validation_from_ai(poem_line, line_number, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on the specific poem type.
    It explicitly ensures validation is focused on a specific line number.
    """
    # Call the specific validation function based on the poem type ID
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
    # Define the Haiku structure
    poem_structure = "5-7-5 syllable structure (Haiku)"
    
    # Construct a prompt for Haiku validation
    prompt = f"""
    You are an expert poetry validator. Given the following poem structure: {poem_structure}, validate the following line.
    
    Poem line: "{poem_line}"

    Validation criteria: 5-7-5 syllable structure.

    Please confirm if this line follows the required syllable structure for line {line_number}.
    - For Haiku, the structure is 5-7-5 (5 syllables for the first line, 7 for the second, and 5 for the third).

    If the line follows the required structure, respond with 'Pass'.
    If the line does not meet the criteria, respond with 'Fail' and provide a concise explanation, 
    specifically noting the syllable count for the given line and why it doesn't match the expected count.
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
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Low temperature for more deterministic responses
            top_k=5,  # Consider the top 5 tokens at each step for focused generation
            top_p=0.9,  # Use tokens that cover 90% of the probability mass, balancing diversity and coherence
            max_tokens=100  # Limit the response length to 100 tokens, which should be sufficient for validation
        )

        # Log the response for debugging
        logging.debug(f"Full response: {response}")

        choices = response.choices
        if choices and len(choices) > 0:
            message = choices[0].message.content.strip()
            logging.debug(f"Validating Haiku line {line_number}: '{poem_line}'")
            return message
        else:
            logging.error("Error: 'choices' missing or empty in response.")
            return "Error: No choices in response."

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
    

def fetch_nonet_validation_from_ai(poem_line, line_number):
    """
    Sends a Nonet poem line to OpenAI's API for validation based on the 9-8-7-6-5-4-3-2-1 syllable structure.
    """
    # Define the Nonet structure
    poem_structure = "Nonet poem with syllable count decreasing from 9 to 1 for each line."
    
    # Construct a prompt for Nonet validation
    prompt = f"""
    You are an expert poetry validator. Given the following poem structure: {poem_structure}, validate the following line.
    
    Poem line: "{poem_line}"

    Validation criteria: 9-8-7-6-5-4-3-2-1 syllable structure.

    Please confirm if this line follows the required syllable structure for line {line_number}.
    - For Nonet, the syllable count decreases from 9 to 1 per line: 9 syllables for the first line, 8 for the second, down to 1 for the last line.

    If the line follows the required structure, respond with 'Pass'.
    If the line does not meet the criteria, respond with 'Fail' and provide a concise explanation, 
    specifically noting the syllable count for the given line and why it doesn't match the expected count.
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
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Low temperature for more deterministic responses
            top_k=5,  # Consider the top 5 tokens at each step for focused generation
            top_p=0.9,  # Use tokens that cover 90% of the probability mass, balancing diversity and coherence
            max_tokens=100  # Limit the response length to 100 tokens, which should be sufficient for validation
        )

        # Log the response for debugging
        logging.debug(f"Full response: {response}")

        choices = response.choices
        if choices and len(choices) > 0:
            message = choices[0].message.content.strip()
            logging.debug(f"Validating Nonet line {line_number}: '{poem_line}'")
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
    # expected_syllables = 9 - (line_number - 1)  # For Nonet: 9, 8, 7, 6, ..., 1

    # Compare NLTK result with expected syllable count for the current line
    if nltk_syllable_count == expected_syllables:
        logging.info(f"NLTK fallback passed for line {line_number}. Syllables matched the {expected_syllables}-syllable structure.")
        return "Pass"
    else:
        logging.error(f"NLTK fallback failed for line {line_number}: Expected {expected_syllables} syllables, got {nltk_syllable_count}.")
        return f"Fail - NLTK counted {nltk_syllable_count} syllables, expected {expected_syllables}."
    