import os
from flask import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv
from .poem_utils import get_poem_type_by_id


load_dotenv()


def fetch_poem_validation(poem_line, criteria, poem_type_id):
    """
    Sends a poem line to OpenAI's API for validation based on poem type criteria.
    """
    # Get the poem type with its criteria
    poem_type = get_poem_type_by_id(poem_type_id)
    context = {'rhyme_scheme': 'AABBA', 'syllable_structure': None}
    if not poem_type:
        return "Error: Poem type not found."

    # Construct a prompt based on the poem type's criteria
    # prompt = f"Please check if this line follows the criteria: {poem_line}. Be very concise and specific with your answer. Respond with either 'Pass' or 'Fail'.\n"
    prompt = f"""Given the following criteria for Limerick poem:
    {context}

    And the Poem with the following line(s):
    {poem_line}
    Please check if the Poem meets the given criteria. 
    Limerick requires 5 lines but please ignore this requirements for now since this is a work in progress.
    Ignore validation if a line introduces a new rhyme. Respond with either 'Pass' or 'Fail', with a concise explanation when it fails."""

    # if 'syllable_structure' in criteria and criteria['syllable_structure']:
        # prompt += f"Syllable structure: {criteria['syllable_structure']}.\n"

    # if 'rhyme_scheme' in criteria and criteria['rhyme_scheme']:
        # prompt += f"Rhyme scheme: {criteria['rhyme_scheme']}.\n"

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        # Make the call to the GPT model
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=messages)

        # Extract the assistant's reply from the response
        print(response)
        reply = response

        return reply.strip()

    except Exception as e:
        print(e)
        return f"Error: {str(e)}"
