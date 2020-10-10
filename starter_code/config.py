import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
#SQLALCHEMY_DATABASE_URI = '<Put your local database url>'

dbname = 'project1'
db_user = 'udacity'
db_pw = 'pwabc'
SQLALCHEMY_DATABASE_URI = f'postgresql://{db_user}:{db_pw}@localhost:5432/{dbname}'

SQLALCHEMY_TRACK_MODIFICATIONS = False
