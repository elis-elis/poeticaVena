import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'one_more_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_SERVER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
