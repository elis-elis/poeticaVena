from .models import Poem, PoemType, PoemDetails


def get_poem_type_by_id(poem_type_id):
    """
    Fetch a poem type by its ID from the database.
    """
    return PoemType.query.get(poem_type_id)


def get_poem_by_id(poem_id):
    """
    Fetch a poem by its ID from the database.
    """
    return Poem.query.get(poem_id)


def get_poem_contributions(poem_id):
    """
    Count how many contributions exist for a specific poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).count()


def get_last_contribution(poem_id):
    """
    Fetch the most recent contribution to a collaborative poem.
    """
    return PoemDetails.query.filter_by(poem_id=poem_id).order_by(PoemDetails.submitted_at.desc()).first()
