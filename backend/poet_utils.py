from flask_jwt_extended import get_jwt_identity
from backend.database import db
from backend.models import Poet, PoemDetails



def get_current_poet():
    """
    Fetch the currently logged-in poet from the database using their poet ID from JWT.
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
    

def get_all_poets():
    """
    Fetch all poets from the database.
    """
    return Poet.query.all()


def get_poet_contributions(poet_id):
    """
    Fetch all contributions made by a specific poet.
    """
    return PoemDetails.query.filet_by(poet_id=poet_id).all()
