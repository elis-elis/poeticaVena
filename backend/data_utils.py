from .database import db
from sqlalchemy.exc import SQLAlchemyError  # SQLAlchemy exception base class


def add_poem_type(name, description, criteria):
    """
    Utility function to add a poem type to the database.
    """
    from .models import PoemType    # Import model only when needed to avoid circular imports
    
    try:
        # Create a new PoemType instance
        new_poem_type = PoemType(
            name=name,
            description=description,
            criteria=criteria
        )

        db.session.add(new_poem_type)
        db.session.commit()

        print(f"Poem type '{name}' added.")
    except SQLAlchemyError as e:
        # Roll back the session in case of any error to avoid inconsistent database state
        db.session.rollback()
        print(f"Error adding poem type '{name}: e")
        return False
    
    return True


def initialize_poem_types():
    """
    Utility function to initialize default poem types if they don't already exist.
    """
    from .models import PoemType

    poem_types = [
        ('Haiku', 'A Japanese unrhymed poem format consisting of 17 syllables arranged in three lines. Often focusing on images from nature, it emphasizes simplicity, intensity, and directness of expression.', '3 lines, syllable structure 5-7-5')
        ('Nonet', 'Poem of nine lines with each line having one syllable less. It can be on any subject and rhyming is optional.', '9 lines, decreasing syllable count from 9 to 1')
        ('Limerick', 'A five line poem with a rhyming pattern of AABBA. It usually tells the tale of someone doing something or something happening to them. It is usually written in a humorous way, and the third and fourth lines are usually shorter than the first, second and fith.', '5 lines, with an AABBA rhyme scheme')
    ]

    for name, description, criteria in poem_types:
        if not PoemType.query.filter_by(name=name).first():
            add_poem_type(name, description, criteria)

    print('Poem types initialized (if not already present).')
    