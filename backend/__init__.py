"""
Application factory and app setup
Uses DATABASE_URL (e.g., Supabase Postgres) if present.
Initializes scheduler for reminders.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from flask_login import LoginManager

from .scheduler import init_scheduler
from .extensions import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Basic config
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Use DATABASE_URL (Supabase) if provided, else fallback to sqlite instance
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        import os as _os
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+_os.path.join(app.instance_path, 'todo.db')

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # register blueprints
    from . import api, web, auth
    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)
    app.register_blueprint(auth.bp)

    # Initialize scheduler for reminders (only if APScheduler available)
    try:
        init_scheduler(app)
    except Exception as e:
        # scheduler is non-critical in dev if dependencies missing
        app.logger.info(f"Scheduler not initialized: {e}")

    return app
