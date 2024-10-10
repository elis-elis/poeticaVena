import os
from flask import json
import openai
from dotenv import load_dotenv


load_dotenv()
openai.my_api_key = os.getenv("OPENAI_API_KEY")


def check_ai_validation(content, poem_type_criteria, poem_id):
    """
    This function checks if the submitted content passes the poem type's criteria:
    - Line length
    - Max number of lines
    - Rhyme scheme
    """
    # Extract the criteria from the poem type
    criteria = json.loads(poem_type_criteria)

    # Check max lines
    pass

