import os

class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    
    # Set the debug mode based on the environment variable
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    
    # Database URI (we'll load this from the .env file as well)
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "mysql://root:@localhost/monitoring_ged")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional, disable unnecessary tracking
