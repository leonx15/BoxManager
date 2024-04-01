from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    Session(app)

    # Register blueprints
    from .blueprints.routes_main import main as main_blueprint
    from .blueprints.routes_boxes import boxes as boxes_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(boxes_blueprint)

    with app.app_context():
        db.create_all()  # Create database tables if not already created

    return app
