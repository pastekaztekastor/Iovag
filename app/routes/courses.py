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


@bp.route('/<int:id>/update-quantite', methods=['POST'])
@login_required
def update_quantite(id):
    """Mettre à jour la quantité achetée d'un ingrédient (AJAX)"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.get_json()
    item_id = data.get('item_id')
    quantite_achetee = data.get('quantite_achetee')

    item = ListeCourseItem.query.get_or_404(item_id)
    if item.liste_id != liste.id:
        return jsonify({'success': False, 'error': 'Item not in list'}), 403

    try:
        item.quantite_achetee = float(quantite_achetee)
        db.session.commit()
        return jsonify({'success': True, 'quantite_achetee': item.quantite_achetee})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid quantity'}), 400


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer une liste de courses"""
    liste = ListeCourse.query.get_or_404(id)
    db.session.delete(liste)
    db.session.commit()
    flash('Liste de courses supprimée avec succès', 'success')
    return redirect(url_for('courses.index'))


@bp.route('/<int:id>/reviser')
@login_required
def reviser(id):
    """Page de révision de la liste avec vérification automatique du stock"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut != 'brouillon':
        flash('Seules les listes en brouillon peuvent être révisées', 'warning')
        return redirect(url_for('courses.detail', id=id))

    # Vérifier le stock automatiquement
    liste.verifier_stock()
    db.session.commit()

    return render_template('courses/reviser.html', liste=liste)


@bp.route('/<int:id>/verifier')
@login_required
def verifier(id):
    """Page de vérification physique (étape 2) - tri par lieu de rangement"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut != 'validee':
        flash('Seules les listes validées peuvent être vérifiées', 'warning')
        return redirect(url_for('courses.detail', id=id))

    return render_template('courses/verifier.html', liste=liste)


@bp.route('/<int:id>/retirer-item/<int:item_id>', methods=['POST'])
@login_required
def retirer_item(id, item_id):
    """Retirer un article de la liste (AJAX)"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    if liste.statut not in ['brouillon', 'validee']:
        return jsonify({'success': False, 'error': 'Liste en cours ou terminée'}), 400

    from app.models import ListeCourseItem
    item = ListeCourseItem.query.get_or_404(item_id)

    if item.liste_id != liste.id:
        return jsonify({'success': False, 'error': 'Item not in list'}), 403

    db.session.delete(item)
    db.session.commit()

    return jsonify({'success': True})


@bp.route('/<int:id>/retirer-items-en-stock', methods=['POST'])
@login_required
def retirer_items_en_stock(id):
    """Retirer tous les articles dont le stock est suffisant"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut not in ['brouillon', 'validee']:
        flash('Cette action n\'est possible que pour les listes en brouillon ou validées', 'warning')
        return redirect(url_for('courses.detail', id=id))

    # Retirer les items en stock
    nb_retires = liste.retirer_items_en_stock()
    db.session.commit()

    if nb_retires > 0:
        flash(f'{nb_retires} article(s) en stock retiré(s) de la liste', 'success')
    else:
        flash('Aucun article à retirer (pas de stock suffisant)', 'info')

    return redirect(url_for('courses.detail', id=id))


@bp.route('/<int:id>/valider', methods=['POST'])
@login_required
def valider(id):
    """Valider la liste de courses (prête pour les courses)"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut == 'confirmee':
        flash('Cette liste a déjà été confirmée', 'warning')
        return redirect(url_for('courses.detail', id=id))

    liste.valider()
    db.session.commit()
    flash('Liste de courses validée et prête pour les courses!', 'success')
    return redirect(url_for('courses.detail', id=id))


@bp.route('/<int:id>/commencer', methods=['POST'])
@login_required
def commencer(id):
    """Commencer les courses (passage en magasin)"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut != 'validee':
        flash('La liste doit être validée avant de commencer les courses', 'warning')
        return redirect(url_for('courses.detail', id=id))

    liste.commencer_courses()
    db.session.commit()
    flash('Bonnes courses! Vous pouvez maintenant ajuster les quantités achetées.', 'success')
    return redirect(url_for('courses.detail', id=id))


@bp.route('/<int:id>/confirmer', methods=['POST'])
@login_required
def confirmer(id):
    """Confirmer l'achat et mettre à jour le stock"""
    liste = ListeCourse.query.get_or_404(id)

    if liste.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette liste', 'danger')
        return redirect(url_for('courses.index'))

    if liste.statut == 'brouillon':
        flash('Vous devez d\'abord valider la liste avant de la confirmer', 'warning')
        return redirect(url_for('courses.detail', id=id))

    if liste.statut == 'validee':
        flash('Vous devez d\'abord commencer les courses', 'warning')
        return redirect(url_for('courses.detail', id=id))

    if liste.statut == 'terminee':
        flash('Cette liste a déjà été terminée', 'warning')
        return redirect(url_for('courses.detail', id=id))

    liste.confirmer()
    db.session.commit()
    flash('Achats confirmés! Le stock a été mis à jour avec les quantités achetées.', 'success')
    return redirect(url_for('courses.detail', id=id))


@bp.route('/<int:id>/export-pdf')
@login_required
def export_pdf(id):
    """Exporter la liste de courses en PDF"""
    # TODO: Implémenter l'export PDF avec WeasyPrint
    flash('Fonctionnalité à venir', 'info')
    return redirect(url_for('courses.detail', id=id))
