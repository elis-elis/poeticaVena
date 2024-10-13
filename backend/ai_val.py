import os
from flask import json
import openai
from dotenv import load_dotenv
from .poem_utils import get_poem_type_by_id


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def fetch_poem_validation(poem_line, criteria, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on poem type criteria.
    """
    # Get the poem type with its criteria
    poem_type = get_poem_type_by_id(poem_type_id)
    if not poem_type:
        return "Error: Poem type not found."

    # Construct a prompt based on the poem type's criteria
    prompt = f"Please check if this line follows the criteria: {poem_line}. Be very concise and specific with your answer. Respond with either 'Pass' or 'Fail'.\n"

    if 'syllable_structure' in criteria and criteria['syllable_structure']:
        prompt += f"Syllable structure: {criteria['syllable_structure']}.\n"

    if 'rhyme_scheme' in criteria and criteria['rhyme_scheme']:
        prompt += f"Rhyme scheme: {criteria['rhyme_scheme']}.\n"

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        # Make the call to the GPT model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Extract the assistant's reply from the response
        reply = response['choices'][0]['message']['content']

        return reply.strip()

    except Exception as e:
        return f"Error: {str(e)}"
        