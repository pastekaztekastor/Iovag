"""
Routes pour la gestion des listes de courses
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ListeCourse, ListeCourseItem, Menu

bp = Blueprint('courses', __name__, url_prefix='/courses')


@bp.route('/')
@login_required
def index():
    """Liste de toutes les listes de courses"""
    listes = ListeCourse.query.filter_by(created_by=current_user.id)\
        .order_by(ListeCourse.created_at.desc()).all()
    return render_template('courses/index.html', listes=listes)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'une liste de courses"""
    liste = ListeCourse.query.get_or_404(id)
    return render_template('courses/detail.html', liste=liste)


@bp.route('/<int:id>/toggle-ingredient', methods=['POST'])
@login_required
def toggle_ingredient(id):
    """Marquer un ingrédient comme acheté/non acheté (AJAX)"""
    liste = ListeCourse.query.get_or_404(id)
    data = request.get_json()
    item_id = data.get('item_id')
    achete = data.get('achete')

    item = ListeCourseItem.query.get_or_404(item_id)
    if item.liste_id != liste.id:
        return jsonify({'success': False, 'error': 'Item not in list'}), 403

    item.achete = achete
    db.session.commit()

    return jsonify({'success': True})


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer une liste de courses"""
    liste = ListeCourse.query.get_or_404(id)
    db.session.delete(liste)
    db.session.commit()
    flash('Liste de courses supprimée avec succès', 'success')
    return redirect(url_for('courses.index'))


@bp.route('/<int:id>/export-pdf')
@login_required
def export_pdf(id):
    """Exporter la liste de courses en PDF"""
    # TODO: Implémenter l'export PDF avec WeasyPrint
    flash('Fonctionnalité à venir', 'info')
    return redirect(url_for('courses.detail', id=id))
