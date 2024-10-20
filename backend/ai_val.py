"""
Handles AI-based validation logic (i.e., sending prompts to the OpenAI API).
"""

import os
from openai import OpenAI
import logging


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv
from .poem_utils import get_poem_type_by_id


load_dotenv()


def fetch_poem_validation_from_ai(poem_line, criteria, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on poem type criteria.
    """
    # Get the poem type with its criteria
    poem_type = get_poem_type_by_id(poem_type_id)
    if not poem_type:
        return "Error: Poem type not found."

    # Construct a prompt based on the poem type's criteria
    prompt = f"""
    You are an expert poetry validator. Given the following criteria: {criteria} for a poem,
    and the following line of the poem:
    {poem_line}
    Please validate the line against the syllable structure.
    - If the poem follows the required syllable structure of 5-7-5, where:
    - The first line must have 5 syllables,
    - The second line must have 7 syllables,
    - The third line must have 5 syllables,
    Then respond with 'Pass'. 
    - If the line does not meet the criteria, respond with 'Fail' and provide a concise explanation, specifically noting which line failed and why.
    Focus on this line only and confirm whether it meets the syllable count requirement as specified in the criteria.
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
            logging.debug(f"Validating line: '{poem_line}' with criteria: {criteria}")
            return message
        else:
            logging.error("Error: 'choices' missing or empty in response.")
            return "Error: No choices in response."

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
