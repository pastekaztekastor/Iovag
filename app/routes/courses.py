"""
Routes pour la gestion des listes de courses
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import ListeCourse, Menu

bp = Blueprint('courses', __name__, url_prefix='/courses')


@bp.route('/')
@login_required
def index():
    """Liste de courses pour un menu donné"""
    menu_id = request.args.get('menu_id', type=int)
    if menu_id:
        menu = Menu.query.get_or_404(menu_id)
        courses = ListeCourse.query.filter_by(menu_id=menu_id).all()
        return render_template('courses/index.html', menu=menu, courses=courses)
    else:
        flash('Veuillez sélectionner un menu', 'warning')
        return redirect(url_for('menus.index'))


@bp.route('/<int:id>/toggle')
@login_required
def toggle(id):
    """Marquer un article comme acheté/non acheté"""
    course = ListeCourse.query.get_or_404(id)
    course.achete = not course.achete
    db.session.commit()
    return redirect(url_for('courses.index', menu_id=course.menu_id))


@bp.route('/export-pdf/<int:menu_id>')
@login_required
def export_pdf(menu_id):
    """Exporter la liste de courses en PDF"""
    # TODO: Implémenter l'export PDF
    flash('Fonctionnalité à venir', 'info')
    return redirect(url_for('courses.index', menu_id=menu_id))
