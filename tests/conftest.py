"""
App Fixture:
Purpose: Initializes your Flask app in a testable state.
How it Works:
Calls create_app() to get a fresh instance of your app.
Configures it with test-specific settings:
TESTING: Activates Flask's testing mode.
SQLALCHEMY_DATABASE_URI: Uses an in-memory SQLite database for isolated testing.
Initializes the database (db.create_all()).
Tears down the database after the tests (db.drop_all()).

Client Fixture:
Purpose: Provides a test client to simulate HTTP requests to your app.
How it Works:
Uses Flask's test_client() method to create a client tied to the app fixture.

Runner Fixture:
Purpose: Provides a CLI runner for testing commands, if needed (e.g., flask db upgrade).
How it Works:
Uses Flask's test_cli_runner() method tied to the app fixture.
"""

import pytest
from backend import create_app
from backend.database import db


@pytest.fixture
def app():
    """
    Create and configure a new app instance for testing.
    """
    app = create_app({
        "TESTING": True,  # Enables testing mode (disables error catching)
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory DB
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()  # Create tables
        yield app   # Provide the app for testing
        db.session.remove()  # Clean up the session
        db.drop_all()   # Drop tables after tests


@pytest.fixture
def client(app):
    """
    A test client for the app.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    A test CLI runner for the app (for testing CLI commands).
    """
    return app.test_cli_runner()
