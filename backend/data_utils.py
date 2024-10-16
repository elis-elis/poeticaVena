import json
from .database import db
from sqlalchemy.exc import SQLAlchemyError  # SQLAlchemy exception base class
from .schemas import PoemTypeResponse


def add_poem_type(name, description, criteria):
    """
    Utility function to add a poem type to the database.
    Returns PoemTypeResponse on success, and False on failure.
    """
    from .models import PoemType    # Import model only when needed to avoid circular imports
    
    try:
        # Convert criteria to a JSON string if it's not already one
        if isinstance(criteria, dict):
            criteria = json.dumps(criteria)

        # Create a new PoemType instance
        new_poem_type = PoemType(
            name=name,
            description=description,
            criteria=criteria   # Store as JSON string
        )

        db.session.add(new_poem_type)
        db.session.commit()

        print(f"Poem type '{name}' added. 🎯")
        # Return the new poem type using the PoemTypeResponse Pydantic model
        poem_type_response = PoemTypeResponse.model_validate(new_poem_type)
        return poem_type_response

    except SQLAlchemyError as e:
        # Roll back the session in case of any error to avoid inconsistent database state
        db.session.rollback()
        print(f"Error adding poem type '{name}: e")
        return False
    

def initialize_poem_types():
    """
    Utility function to initialize default poem types if they don't already exist.
    """
    from .models import PoemType

    poem_types = [
        ('Haiku',
        'A Japanese unrhymed poem format consisting of 17 syllables arranged in three lines. Often focusing on images from nature, it emphasizes simplicity, intensity, and directness of expression.',
        {
            'max_lines': 3,
            'syllable_structure': '5-7-5',
            'rhyme_scheme': None
        }),
        ('Nonet',
        'Poem of nine lines with each line having one syllable less. It can be on any subject and rhyming is optional.',
        {
            'max_lines': 9,
            'syllable_structure': '9-8-7-6-5-4-3-2-1',
            'rhyme_scheme': None
        }),
        ('Limerick',
        'A five line poem with a rhyming pattern of AABBA. It usually tells the tale of someone doing something or something happening to them. It is usually written in a humorous way, and the third and fourth lines are usually shorter than the first, second and fith.',
        {
            'max_lines': 5,
            'syllable_structure': None,
            'rhyme_scheme': 'AABBA'
        }),
    ]

    for name, description, criteria in poem_types:
        # Check if the poem type already exists
        if not PoemType.query.filter_by(name=name).first():
            # Save criteria as JSON string in the database
            add_poem_type(name, description, criteria)

    print('Poem types initialized (if not already present). 🍬')
