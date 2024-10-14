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
    if not poem_type:
        return "Error: Poem type not found."

    # Construct a prompt based on the poem type's criteria
    prompt = f""" Given the following criteria {criteria} for a poem:
    and the Poem with the following line(s):
    {poem_line}
    Please check if the Poem meets the given criteria.
    consider that it is work in progress and so each line should be checked separately by syllable count and not by lines count. if syllable structure is 5-7-5 and the first line has 5 syllables it means the line should pass validation.
    Respond with either 'Pass' or 'Fail', with a concise explanation when it fails."""

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Print the response structure
        print(f"Full response: {response}")
        print(f"Response type: {type(response)}")

        choices = response.choices
        if choices and len(choices) > 0:
            message = choices[0].message.content.strip()
            print(f"Reply from GPT: {message}")  # Now print the extracted message
            return message
        else:
            print("Error: 'choices' missing or empty in response.")
            return "Error: No choices in response."

    except Exception as e:
        return f"Error: {str(e)}"
