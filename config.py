import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_PATH = os.path.join(BASEDIR, 'instance')
DB_PATH = os.path.join(INSTANCE_PATH, 'ppat.db')

class Config:
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
