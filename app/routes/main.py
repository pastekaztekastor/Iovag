"""
Routes principales de l'application
"""
from flask import Blueprint, render_template
from flask_login import current_user
from app.models import Menu, Recette

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        # Récupérer les menus et recettes récents de l'utilisateur
        menus_recents = Menu.query.filter_by(created_by=current_user.id)\
            .order_by(Menu.created_at.desc()).limit(6).all()
        recettes_favorites = Recette.query.filter_by(created_by=current_user.id)\
            .filter(Recette.evaluation >= 4)\
            .order_by(Recette.evaluation.desc()).limit(6).all()

        return render_template('index.html',
                             menus_recents=menus_recents,
                             recettes_favorites=recettes_favorites)
    else:
        return render_template('landing.html')


@bp.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html')
