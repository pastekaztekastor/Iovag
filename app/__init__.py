"""
Factory pour créer l'application Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import os

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Factory pour créer l'application Flask

    Args:
        config_name: Nom de la configuration à utiliser (development, production, testing)

    Returns:
        Flask app instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_OUTPUT_DIR'], exist_ok=True)
    os.makedirs(app.root_path.replace('app', 'instance'), exist_ok=True)

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    # Importer les modèles
    from app import models

    # Enregistrer les blueprints
    from app.routes import auth, menus, recettes, courses, main, ingredients

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(recettes.bp)
    app.register_blueprint(menus.bp)
    app.register_blueprint(courses.bp)
    app.register_blueprint(ingredients.bp)

    # Contexte du processeur de template
    @app.context_processor
    def utility_processor():
        """Fonctions utilitaires disponibles dans tous les templates"""
        return {
            'app_name': 'Iovag',
            'app_tagline': 'Ici on veille à la gourmandise'
        }

    return app
