"""
Routes pour la gestion des menus
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Menu, MenuJour, Recette

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
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form.get('nom')
        date_debut_str = request.form.get('date_debut')
        nb_personnes = request.form.get('nb_personnes', type=int)
        theme = request.form.get('theme')
        description = request.form.get('description')

        # Convertir la date
        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()

        # Créer le menu
        menu = Menu(
            nom=nom,
            date_debut=date_debut,
            nb_personnes=nb_personnes,
            theme=theme if theme else None,
            description=description if description else None,
            created_by=current_user.id
        )
        db.session.add(menu)
        db.session.flush()  # Pour obtenir l'ID du menu

        # Traiter les 7 jours de la semaine
        for jour in range(7):
            petit_dejeuner_id = request.form.get(f'jour_{jour}_petit_dejeuner')
            dejeuner_id = request.form.get(f'jour_{jour}_dejeuner')
            diner_id = request.form.get(f'jour_{jour}_diner')

            # Créer le MenuJour seulement s'il y a au moins un repas
            if petit_dejeuner_id or dejeuner_id or diner_id:
                menu_jour = MenuJour(
                    menu_id=menu.id,
                    jour_semaine=jour,
                    petit_dejeuner_id=int(petit_dejeuner_id) if petit_dejeuner_id else None,
                    dejeuner_id=int(dejeuner_id) if dejeuner_id else None,
                    diner_id=int(diner_id) if diner_id else None
                )
                db.session.add(menu_jour)

        db.session.commit()
        flash('Menu créé avec succès', 'success')
        return redirect(url_for('menus.detail', id=menu.id))

    # GET: Récupérer toutes les recettes de l'utilisateur pour les dropdowns
    recettes = Recette.query.filter_by(created_by=current_user.id)\
        .order_by(Recette.nom).all()

    # Date du jour au format ISO (YYYY-MM-DD)
    today = datetime.now().date().isoformat()

    return render_template('menus/create.html', recettes=recettes, today=today)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier un menu"""
    menu = Menu.query.get_or_404(id)

    if request.method == 'POST':
        # Mettre à jour les informations générales
        menu.nom = request.form.get('nom')
        date_debut_str = request.form.get('date_debut')
        menu.date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        menu.nb_personnes = request.form.get('nb_personnes', type=int)
        menu.theme = request.form.get('theme') or None
        menu.description = request.form.get('description') or None

        # Supprimer les anciens jours
        MenuJour.query.filter_by(menu_id=menu.id).delete()

        # Recréer les jours avec les nouvelles valeurs
        for jour in range(7):
            petit_dejeuner_id = request.form.get(f'jour_{jour}_petit_dejeuner')
            dejeuner_id = request.form.get(f'jour_{jour}_dejeuner')
            diner_id = request.form.get(f'jour_{jour}_diner')

            # Créer le MenuJour seulement s'il y a au moins un repas
            if petit_dejeuner_id or dejeuner_id or diner_id:
                menu_jour = MenuJour(
                    menu_id=menu.id,
                    jour_semaine=jour,
                    petit_dejeuner_id=int(petit_dejeuner_id) if petit_dejeuner_id else None,
                    dejeuner_id=int(dejeuner_id) if dejeuner_id else None,
                    diner_id=int(diner_id) if diner_id else None
                )
                db.session.add(menu_jour)

        db.session.commit()
        flash('Menu modifié avec succès', 'success')
        return redirect(url_for('menus.detail', id=menu.id))

    # GET: Récupérer toutes les recettes de l'utilisateur
    recettes = Recette.query.filter_by(created_by=current_user.id)\
        .order_by(Recette.nom).all()
    return render_template('menus/edit.html', menu=menu, recettes=recettes)


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
    liste_course = menu.generer_liste_courses()
    db.session.commit()
    flash('Liste de courses générée avec succès', 'success')
    return redirect(url_for('courses.detail', id=liste_course.id))
