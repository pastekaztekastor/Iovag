"""
Routes pour la gestion des recettes
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Recette

bp = Blueprint('recettes', __name__, url_prefix='/recettes')


@bp.route('/')
@login_required
def index():
    """Liste des recettes"""
    recettes = Recette.query.filter_by(created_by=current_user.id).all()
    return render_template('recettes/index.html', recettes=recettes)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'une recette"""
    recette = Recette.query.get_or_404(id)
    return render_template('recettes/detail.html', recette=recette)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Créer une nouvelle recette"""
    # TODO: Implémenter le formulaire et la création
    return render_template('recettes/create.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier une recette"""
    recette = Recette.query.get_or_404(id)
    # TODO: Implémenter le formulaire et la modification
    return render_template('recettes/edit.html', recette=recette)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer une recette"""
    recette = Recette.query.get_or_404(id)
    db.session.delete(recette)
    db.session.commit()
    flash('Recette supprimée avec succès', 'success')
    return redirect(url_for('recettes.index'))
