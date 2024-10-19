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
        ('Free Verse',
        'A poem that does not follow any specific meter, rhyme scheme, or structure. It allows for complete freedom of expression.',
        {
            'max_lines': None,  # No limit on lines
            'syllable_structure': None,  # No syllable restrictions
            'rhyme_scheme': None  # No rhyme scheme
        }),
    ]

    for name, description, criteria in poem_types:
        # Check if the poem type already exists
        if not PoemType.query.filter_by(name=name).first():
            # Save criteria as JSON string in the database
            add_poem_type(name, description, criteria)

    print('Poem types initialized (if not already present). 🍬')


def delete_poem_type_by_name(name):
    from .models import PoemType, Poem
    # Fetch the poem type to delete
    poem_type = PoemType.query.filter_by(name=name).first()

    if poem_type:
        # Fetch poems associated with this poem_type (e.g., Limerick)
        poems_with_this_type = Poem.query.filter_by(poem_type_id=poem_type.id).all()

        if poems_with_this_type:
            # Find the "Free Verse" type
            free_verse_type = PoemType.query.filter_by(name='Free Verse').first()

            if not free_verse_type:
                print(f"'Free Verse' poem type not found! Please create 'Free Verse' first.")
                return False

            # Reassign all poems to "Free Verse"
            for poem in poems_with_this_type:
                poem.poem_type_id = free_verse_type.id

        # Now, it's safe to delete the "Limerick" poem type
        db.session.delete(poem_type)
        db.session.commit()

        print(f"Poem type '{name}' has been deleted and poems reassigned to 'Free Verse'. 🍂")
    else:
        print(f"Poem type '{name}' not found. 🚫")


def delete_unnecessary_poem_type(name):
    """
    Utility function to delete an unnecessary poem type like 'Unspecified' if it was created by mistake.
    """
    from .models import PoemType
    poem_type = PoemType.query.filter_by(name=name).first()

    if poem_type:
        db.session.delete(poem_type)
        db.session.commit()
        print(f"Poem type '{name}' has been deleted. 🗑️")
    else:
        print(f"Poem type '{name}' not found. 🚫")
