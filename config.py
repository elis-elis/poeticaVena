class Config:
    SECRET_KEY = 'secret_key_is_secret'
    SQLALCHEMY_DATABASE_URI = f'postgresql://elisnothing:1234@localhost:5432/poeticaVENA_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
