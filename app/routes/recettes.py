"""
Routes pour la gestion des recettes
"""
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Recette, Ingredient, RecetteIngredient, Instruction

bp = Blueprint('recettes', __name__, url_prefix='/recettes')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form.get('nom')
        portions = request.form.get('portions', type=int)
        temps_preparation = request.form.get('temps_preparation')
        temps_cuisson = request.form.get('temps_cuisson')
        auteur_nom = request.form.get('auteur_nom')
        evaluation = request.form.get('evaluation', type=int, default=0)
        note = request.form.get('note')

        # Gérer l'upload de la photo
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Créer un nom unique avec timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"

                # Créer le dossier uploads s'il n'existe pas
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recettes')
                os.makedirs(upload_folder, exist_ok=True)

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                photo_url = f"/static/uploads/recettes/{filename}"

        # Créer la recette
        recette = Recette(
            nom=nom,
            portions=portions,
            temps_preparation=temps_preparation if temps_preparation else None,
            temps_cuisson=temps_cuisson if temps_cuisson else None,
            auteur_nom=auteur_nom if auteur_nom else None,
            evaluation=evaluation,
            note=note if note else None,
            photo_url=photo_url,
            created_by=current_user.id
        )
        db.session.add(recette)
        db.session.flush()  # Pour obtenir l'ID de la recette

        # Traiter les ingrédients
        quantites = request.form.getlist('ingredient_quantite[]')
        unites = request.form.getlist('ingredient_unite[]')
        noms = request.form.getlist('ingredient_nom[]')

        for i, nom_ingredient in enumerate(noms):
            if nom_ingredient.strip():  # Ignorer les lignes vides
                # Chercher ou créer l'ingrédient
                ingredient = Ingredient.query.filter_by(nom=nom_ingredient.strip()).first()
                if not ingredient:
                    ingredient = Ingredient(nom=nom_ingredient.strip())
                    db.session.add(ingredient)
                    db.session.flush()

                # Créer le lien recette-ingrédient
                try:
                    quantite = float(quantites[i]) if i < len(quantites) and quantites[i].strip() else 0
                except (ValueError, AttributeError):
                    quantite = 0
                unite = unites[i].strip() if i < len(unites) and unites[i] else ''

                recette_ingredient = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=quantite,
                    unite=unite
                )
                db.session.add(recette_ingredient)

        # Traiter les instructions
        instructions_textes = request.form.getlist('instruction[]')
        for ordre, texte in enumerate(instructions_textes, start=1):
            if texte.strip():  # Ignorer les lignes vides
                instruction = Instruction(
                    recette_id=recette.id,
                    ordre=ordre,
                    texte=texte.strip()
                )
                db.session.add(instruction)

        db.session.commit()
        flash('Recette créée avec succès', 'success')
        return redirect(url_for('recettes.detail', id=recette.id))

    return render_template('recettes/create.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier une recette"""
    recette = Recette.query.get_or_404(id)

    if request.method == 'POST':
        # Mettre à jour les informations générales
        recette.nom = request.form.get('nom')
        recette.portions = request.form.get('portions', type=int)
        recette.temps_preparation = request.form.get('temps_preparation') or None
        recette.temps_cuisson = request.form.get('temps_cuisson') or None
        recette.auteur_nom = request.form.get('auteur_nom') or None
        recette.evaluation = request.form.get('evaluation', type=int, default=0)
        recette.note = request.form.get('note') or None

        # Gérer l'upload d'une nouvelle photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"

                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recettes')
                os.makedirs(upload_folder, exist_ok=True)

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                recette.photo_url = f"/static/uploads/recettes/{filename}"

        db.session.commit()
        flash('Recette modifiée avec succès', 'success')
        return redirect(url_for('recettes.detail', id=recette.id))

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
