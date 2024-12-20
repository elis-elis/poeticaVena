from flask_jwt_extended import get_jwt_identity
from backend.models import Poet, PoemDetails
from .database import db


def fetch_poet(poet_id):
    """
    This function that retrieves a poet from the database by their ID, regardless of the logged-in user.
    """
    return Poet.query.filter_by(id=poet_id).first()


def get_current_poet():
    """
    Fetch the currently logged-in poet from the database using their poet ID from JWT.
    """
    poet_object = get_jwt_identity()
    print(f"DEBUG: Token Payload in get_current_poet -> {poet_object}")

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


def get_all_poets_query():
    """
    Returns a query object for fetching all poets from the database.
    """
    return Poet.query


def get_poet_contributions(poet_id):
    """
    Fetch all contributions made by a specific poet.
    """
    return PoemDetails.query.filet_by(poet_id=poet_id).all()


def get_or_create_deleted_poet():
    """
    Helper function to get or create the anonymous poet.
    """
    deleted_poet = Poet.query.filter_by(email='deletedpoet@gmail.com').first()
    if not deleted_poet:
        deleted_poet = Poet(
            poet_name='deletedPoet', 
            email='deletedpoet@gmail.com', 
            password_hash='deleted'
        )
        db.session.add(deleted_poet)
        db.session.commit()
    return deleted_poet.id  # Return the ID of the existing or newly created poet
