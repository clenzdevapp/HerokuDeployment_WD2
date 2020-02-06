import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))  # this connects to a database either on Heroku or on localhost


class CompetitionUser(db.Model):
    # IN DIESER KLASSE WIRD DAS DATENBANKMODELL User MODELLIERT
    id = db.Column(db.Integer, primary_key=True)    #Primärschlüssel
    name = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    songtitle = db.Column(db.String, unique=False)

class User(db.Model):
    # IN DIESER KLASSE WIRD DAS DATENBANKMODELL User MODELLIERT
    id = db.Column(db.Integer, primary_key=True)    #Primärschlüssel
    username = db.Column(db.String, unique=False)
    name = db.Column(db.String, unique=False)
    password = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=False)
    session_token = db.Column(db.String, unique=False)