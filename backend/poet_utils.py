from backend.database import db
from backend.models import Poet

def get_poet_by_email(poet_email):
    """
    Fetch a poet from the database using their email.
    """
    # Use SQLAlchemy to filter the Poet table by email
    poet = Poet.query.filter_by(email=poet_email).first()

    # If poet is found, return the poet object
    if poet:
        return poet
    else:
        # If no poet is found, raise an exception or handle the error accordingly
        raise ValueError(f"No poet found with email {poet_email}")
    