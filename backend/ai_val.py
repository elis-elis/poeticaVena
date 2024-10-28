import os
from openai import OpenAI
import logging
from dotenv import load_dotenv


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
    print(f"Fetching validation for line: '{poem_line}' with line number: {line_number}")

    prompt = f"""
    You are an expert in poetry validation, focusing on syllable counting accuracy. 
    Your task is to validate the syllable count of a Haiku line based on the traditional 5-7-5 syllable structure.
    
    Carefully count syllables for each word, considering common syllabic patterns for repetitions and ignoring punctuation.

    Line to analyze: "{poem_line}"
    Line number in Haiku: {line_number} (1 = 5 syllables, 2 = 7 syllables, 3 = 5 syllables).

    If the line exactly meets the required syllable count, respond with only 'Pass'.
    If it does not, respond with 'Fail' and explain the syllable count in one concise sentence, noting the total syllables you counted.
    """
    print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
    print(prompt)
    print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")

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
    If it does not, respond with 'Fail' and concisely explain the syllable count issue.
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
            # temperature=0.3,
        )

        # Debug print the entire response
        print("API Response:", response)

        choices = response.choices
        if choices and len(choices) > 0:
            response_content = choices[0].message.content.strip()
            if "Pass" in response_content:
                return "Pass"
            elif "Fail" in response_content:
                return f"{response_content}"
            else:
                logging.error(f"Unexpected response content: {response_content}")
                return "Error: Unexpected response from AI."
        else:
            logging.error("Error: 'choices' missing or empty in response.")
            return "Error: No response from AI."
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
