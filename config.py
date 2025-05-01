import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
