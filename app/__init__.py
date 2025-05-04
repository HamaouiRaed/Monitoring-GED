from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # ✅ Add this
from dotenv import load_dotenv
import os
import logging
from config import Config
from flask_jwt_extended import JWTManager

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()  # ✅ Add this
jwt = JWTManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ Add this
    jwt.init_app(app)

    # Register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .routes.login import login as login_blueprint
    app.register_blueprint(login_blueprint)

    from .routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from .routes.logout import logout as logout_blueprint
    app.register_blueprint(logout_blueprint)
    
    from .routes.cards import card as cards_blueprint
    app.register_blueprint(cards_blueprint)
    
    from .routes.bases import base as bases_blueprint
    app.register_blueprint(bases_blueprint)
    
    from .routes.domaines import domaine as domaines_blueprint
    app.register_blueprint(domaines_blueprint)
    
    from .routes.users import user_bp as users_blueprint
    app.register_blueprint(users_blueprint)

    return app
