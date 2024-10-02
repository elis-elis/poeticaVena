from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect


db = SQLAlchemy()

def create_database(app):
    with app.app_context():
        inspector = inspect(db.engine)

        table_names = ['poets', 'poems', 'poem_types', 'poem_details']

        all_tables_exist = True
        for table_name in table_names:
            if not inspector.has_table(table_name):
                all_tables_exist = False
                break
        if all_tables_exist:
            print('Database already exists, skipping table creation.')
        else:
            db.create_all()
            print('Database and tables created! 👑')
            