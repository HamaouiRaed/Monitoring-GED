from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
import config

# Load .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Global extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.Config)

    # Config JWT
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "fallback-jwt")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")  # <- ligne cruciale
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login.handle_login"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_user():
        return {
            "user": {
                "username": session.get("username"),
                "role": session.get("role")
            }
        }

    # Register Blueprints
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

    from .routes.logs import logs_bp
    app.register_blueprint(logs_bp)

    from .routes.manage_users import admin_bp as manage_users_bp
    app.register_blueprint(manage_users_bp)

    from .routes.manage_files import files_bp
    app.register_blueprint(files_bp)

    from .routes.update_pie import update_pie_bp
    app.register_blueprint(update_pie_bp)

    from .routes.streamlit_launcher import run_streamlit
    run_streamlit()

    from .routes.admin import admin as admin_bp
    app.register_blueprint(admin_bp)

    return app


