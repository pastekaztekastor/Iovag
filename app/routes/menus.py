"""
Routes pour la gestion des menus
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Menu

bp = Blueprint('menus', __name__, url_prefix='/menus')


@bp.route('/')
@login_required
def index():
    """Liste des menus"""
    menus = Menu.query.filter_by(created_by=current_user.id)\
        .order_by(Menu.date_debut.desc()).all()
    return render_template('menus/index.html', menus=menus)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'un menu"""
    menu = Menu.query.get_or_404(id)
    return render_template('menus/detail.html', menu=menu)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Créer un nouveau menu"""
    # TODO: Implémenter le formulaire et la création
    return render_template('menus/create.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier un menu"""
    menu = Menu.query.get_or_404(id)
    # TODO: Implémenter le formulaire et la modification
    return render_template('menus/edit.html', menu=menu)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer un menu"""
    menu = Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu supprimé avec succès', 'success')
    return redirect(url_for('menus.index'))


@bp.route('/<int:id>/generer-courses')
@login_required
def generer_courses(id):
    """Générer la liste de courses pour un menu"""
    menu = Menu.query.get_or_404(id)
    menu.generer_liste_courses()
    flash('Liste de courses générée avec succès', 'success')
    return redirect(url_for('courses.index', menu_id=id))
