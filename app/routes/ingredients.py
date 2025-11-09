"""
Routes pour la gestion des ingrédients
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Ingredient

bp = Blueprint('ingredients', __name__, url_prefix='/ingredients')


@bp.route('/')
@login_required
def index():
    """Liste des ingrédients"""
    ingredients = Ingredient.query.order_by(Ingredient.nom).all()
    return render_template('ingredients/index.html',
                         ingredients=ingredients,
                         categories=Ingredient.CATEGORIES,
                         lieux_rangement=Ingredient.LIEUX_RANGEMENT,
                         mois_list=Ingredient.MOIS)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Créer un nouvel ingrédient"""
    if request.method == 'POST':
        nom = request.form.get('nom')
        categorie = request.form.get('categorie')
        unite_mesure = request.form.get('unite_mesure')
        duree_conservation = request.form.get('duree_conservation', type=int)
        lieu_rangement = request.form.get('lieu_rangement')
        stock_limite = request.form.get('stock_limite', type=float)
        poids_estime_g = request.form.get('poids_estime_g', type=float)
        mois_saison = request.form.getlist('mois_saison')  # Liste de mois

        # Vérifier si l'ingrédient existe déjà
        if Ingredient.query.filter_by(nom=nom).first():
            flash('Un ingrédient avec ce nom existe déjà', 'danger')
            return render_template('ingredients/create.html',
                                 categories=Ingredient.CATEGORIES,
                                 lieux_rangement=Ingredient.LIEUX_RANGEMENT,
                                 mois_list=Ingredient.MOIS)

        ingredient = Ingredient(
            nom=nom,
            categorie=categorie if categorie else None,
            unite_mesure=unite_mesure if unite_mesure else None,
            duree_conservation=duree_conservation if duree_conservation else None,
            lieu_rangement=lieu_rangement if lieu_rangement else None,
            stock_limite=stock_limite if stock_limite else None,
            poids_estime_g=poids_estime_g if poids_estime_g else None
        )

        # Définir les mois de saison
        if mois_saison:
            ingredient.set_mois_saison_list(mois_saison)

        db.session.add(ingredient)
        db.session.commit()

        flash('Ingrédient créé avec succès', 'success')
        return redirect(url_for('ingredients.index'))

    return render_template('ingredients/create.html',
                         categories=Ingredient.CATEGORIES,
                         lieux_rangement=Ingredient.LIEUX_RANGEMENT,
                         mois_list=Ingredient.MOIS)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier un ingrédient"""
    ingredient = Ingredient.query.get_or_404(id)

    if request.method == 'POST':
        ingredient.nom = request.form.get('nom')
        ingredient.categorie = request.form.get('categorie') or None
        ingredient.unite_mesure = request.form.get('unite_mesure') or None
        ingredient.duree_conservation = request.form.get('duree_conservation', type=int) or None
        ingredient.lieu_rangement = request.form.get('lieu_rangement') or None
        ingredient.stock_limite = request.form.get('stock_limite', type=float) or None
        ingredient.poids_estime_g = request.form.get('poids_estime_g', type=float) or None

        # Récupérer et définir les mois de saison
        mois_saison = request.form.getlist('mois_saison')
        if mois_saison:
            ingredient.set_mois_saison_list(mois_saison)
        else:
            ingredient.mois_saison = None

        db.session.commit()
        flash('Ingrédient modifié avec succès', 'success')
        return redirect(url_for('ingredients.index'))

    return render_template('ingredients/edit.html',
                         ingredient=ingredient,
                         categories=Ingredient.CATEGORIES,
                         lieux_rangement=Ingredient.LIEUX_RANGEMENT,
                         mois_list=Ingredient.MOIS)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer un ingrédient"""
    ingredient = Ingredient.query.get_or_404(id)

    # Vérifier s'il est utilisé dans des recettes
    if ingredient.recette_ingredients.count() > 0:
        flash('Impossible de supprimer cet ingrédient car il est utilisé dans des recettes', 'danger')
        return redirect(url_for('ingredients.index'))

    db.session.delete(ingredient)
    db.session.commit()
    flash('Ingrédient supprimé avec succès', 'success')
    return redirect(url_for('ingredients.index'))
