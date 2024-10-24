from flask_jwt_extended import get_jwt_identity
from backend.database import db
from backend.models import Poet

def get_current_poet():
    """
    Fetch a poet from the database using their email.
    """
    poet_object = get_jwt_identity()

    # Use SQLAlchemy to filter the Poet table by 
    poet = Poet.query.filter_by(id=poet_object['poet_id']).first()

    # If poet is found, return the poet object
    if poet:
        return poet
    else:
        # If no poet is found, raise an exception or handle the error accordingly
        raise ValueError(f"You are not logged in.")
    