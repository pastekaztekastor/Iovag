"""
Routes pour la gestion des recettes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Recette, Ingredient, RecetteIngredient, Instruction

bp = Blueprint('recettes', __name__, url_prefix='/recettes')


@bp.route('/')
@login_required
def index():
    """Liste des recettes"""
    from datetime import datetime
    recettes = Recette.query.filter_by(created_by=current_user.id).all()
    return render_template('recettes/index.html', recettes=recettes, now=datetime.now())


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

        # Récupérer les mois de saison
        mois_saison_list = request.form.getlist('mois_saison[]')
        mois_saison_str = ','.join(mois_saison_list) if mois_saison_list else None

        # Récupérer les types de repas
        type_repas_list = request.form.getlist('type_repas[]')
        type_repas_str = ','.join(type_repas_list) if type_repas_list else None

        # Créer la recette
        recette = Recette(
            nom=nom,
            portions=portions,
            temps_preparation=temps_preparation if temps_preparation else None,
            temps_cuisson=temps_cuisson if temps_cuisson else None,
            auteur_nom=auteur_nom if auteur_nom else None,
            evaluation=evaluation,
            note=note if note else None,
            mois_saison=mois_saison_str,
            type_repas=type_repas_str,
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

    # Récupérer tous les ingrédients pour l'autocomplétion
    ingredients = Ingredient.query.order_by(Ingredient.nom).all()
    return render_template('recettes/create.html', ingredients=ingredients)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier une recette"""
    recette = Recette.query.get_or_404(id)

    # Vérifier que l'utilisateur est l'auteur
    if recette.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette recette', 'danger')
        return redirect(url_for('recettes.detail', id=id))

    if request.method == 'POST':
        # Mettre à jour les informations générales
        recette.nom = request.form.get('nom')
        recette.portions = request.form.get('portions', type=int)
        recette.temps_preparation = request.form.get('temps_preparation') or None
        recette.temps_cuisson = request.form.get('temps_cuisson') or None
        recette.auteur_nom = request.form.get('auteur_nom') or None
        recette.evaluation = request.form.get('evaluation', type=int, default=0)
        recette.note = request.form.get('note') or None

        # Mettre à jour les mois de saison
        mois_saison_list = request.form.getlist('mois_saison[]')
        recette.mois_saison = ','.join(mois_saison_list) if mois_saison_list else None

        # Mettre à jour les types de repas
        type_repas_list = request.form.getlist('type_repas[]')
        recette.type_repas = ','.join(type_repas_list) if type_repas_list else None

        # Supprimer les ingrédients existants
        RecetteIngredient.query.filter_by(recette_id=recette.id).delete()

        # Ajouter les nouveaux ingrédients
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

        # Supprimer les instructions existantes
        Instruction.query.filter_by(recette_id=recette.id).delete()

        # Ajouter les nouvelles instructions
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
        flash('Recette modifiée avec succès', 'success')
        return redirect(url_for('recettes.detail', id=recette.id))

    # Récupérer tous les ingrédients pour l'autocomplétion
    ingredients = Ingredient.query.order_by(Ingredient.nom).all()
    return render_template('recettes/edit.html', recette=recette, ingredients=ingredients)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer une recette"""
    recette = Recette.query.get_or_404(id)

    # Vérifier que l'utilisateur est l'auteur
    if recette.created_by != current_user.id:
        flash('Vous n\'avez pas la permission de supprimer cette recette', 'danger')
        return redirect(url_for('recettes.detail', id=id))

    db.session.delete(recette)
    db.session.commit()
    flash('Recette supprimée avec succès', 'success')
    return redirect(url_for('recettes.index'))


@bp.route('/api/search')
@login_required
def api_search():
    """
    API de recherche de recettes avec filtres intelligents

    Paramètres:
    - q: terme de recherche (nom de recette ou ingrédient)
    - menu_id: ID du menu (optionnel, pour trier par pertinence)
    - recettes_menu: IDs de recettes séparées par virgule (pour création de menu)
    - mois: mois actuel (1-12) pour indicateur de saison
    - type_repas: type de repas (petit_dejeuner, dejeuner, diner)
    """
    from datetime import datetime

    query_term = request.args.get('q', '').strip()
    menu_id = request.args.get('menu_id', type=int)
    recettes_menu_str = request.args.get('recettes_menu', '')
    mois_actuel = request.args.get('mois', datetime.now().month, type=int)
    type_repas = request.args.get('type_repas', '')

    # Parser les IDs de recettes du menu en cours de création
    recettes_dans_menu = set()
    if recettes_menu_str:
        try:
            recettes_dans_menu = set(int(id_str.strip()) for id_str in recettes_menu_str.split(',') if id_str.strip())
        except ValueError:
            pass

    # Récupérer toutes les recettes de l'utilisateur
    recettes = Recette.query.filter_by(created_by=current_user.id).all()

    resultats = []

    for recette in recettes:
        # Filtrer par terme de recherche (nom ou ingrédient)
        if query_term:
            match_nom = query_term.lower() in recette.nom.lower()
            match_ingredient = any(
                query_term.lower() in ri.ingredient.nom.lower()
                for ri in recette.ingredients
            )

            if not (match_nom or match_ingredient):
                continue

        # Déterminer le statut de saison
        mois_saison_list = recette.get_mois_saison_list()
        mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        mois_nom_actuel = mois_noms[mois_actuel]

        if not mois_saison_list:
            statut_saison = 'toute_saison'
            icone_saison = '🌍'
            couleur_saison = 'secondary'
        elif mois_nom_actuel in mois_saison_list:
            statut_saison = 'de_saison'
            icone_saison = '🌿'
            couleur_saison = 'success'
        else:
            statut_saison = 'hors_saison'
            icone_saison = '❄️'
            couleur_saison = 'warning'

        # Calculer le score de pertinence et les raisons
        score_pertinence = 0
        raisons = []
        ingredients_communs_noms = []
        nb_communs = 0

        # Récupérer les recettes du menu (soit depuis menu_id, soit depuis recettes_menu)
        if menu_id:
            from app.models import Menu, Ingredient
            menu = Menu.query.get(menu_id)
            if menu:
                for jour in menu.jours:
                    if jour.petit_dejeuner_id:
                        recettes_dans_menu.add(jour.petit_dejeuner_id)
                    if jour.dejeuner_id:
                        recettes_dans_menu.add(jour.dejeuner_id)
                    if jour.gouter_id:
                        recettes_dans_menu.add(jour.gouter_id)
                    if jour.diner_id:
                        recettes_dans_menu.add(jour.diner_id)

        # Si on a des recettes dans le menu (édition ou création)
        if recettes_dans_menu:
            # Recette déjà dans le menu = score élevé
            if recette.id in recettes_dans_menu:
                score_pertinence += 1000  # Très haut score
                raisons.append('Déjà dans le menu')

            # Ingrédients en commun avec les recettes du menu
            ingredients_menu = set()
            ingredients_menu_dict = {}  # Pour récupérer les noms
            for recette_id in recettes_dans_menu:
                r = Recette.query.get(recette_id)
                if r:
                    for ri in r.ingredients:
                        ingredients_menu.add(ri.ingredient_id)
                        ingredients_menu_dict[ri.ingredient_id] = ri.ingredient.nom

            ingredients_recette = set(ri.ingredient_id for ri in recette.ingredients)
            ingredients_communs_ids = ingredients_menu.intersection(ingredients_recette)
            nb_communs = len(ingredients_communs_ids)

            if nb_communs > 0:
                score_pertinence += nb_communs * 10
                # Récupérer les noms des ingrédients communs
                ingredients_communs_noms = [ingredients_menu_dict[ing_id] for ing_id in ingredients_communs_ids]
                if nb_communs == 1:
                    raisons.append(f'1 ingrédient commun: {ingredients_communs_noms[0]}')
                elif nb_communs <= 3:
                    raisons.append(f'{nb_communs} ingrédients communs: {", ".join(ingredients_communs_noms)}')
                else:
                    raisons.append(f'{nb_communs} ingrédients communs: {", ".join(ingredients_communs_noms[:3])}, ...')

        # Bonus si de saison
        if statut_saison == 'de_saison':
            score_pertinence += 50
        elif statut_saison == 'toute_saison':
            score_pertinence += 25

        # Bonus si correspond au type de repas
        if type_repas:
            type_repas_map = {
                'petit_dejeuner': 'Petit-déjeuner',
                'dejeuner': 'Déjeuner',
                'gouter': 'Goûter',
                'diner': 'Dîner'
            }
            if type_repas_map.get(type_repas) in recette.get_type_repas_list():
                score_pertinence += 30

        resultats.append({
            'id': recette.id,
            'nom': recette.nom,
            'portions': recette.portions,
            'temps_total': f"{recette.temps_preparation or '?'} + {recette.temps_cuisson or '?'}",
            'evaluation': recette.evaluation,
            'statut_saison': statut_saison,
            'icone_saison': icone_saison,
            'couleur_saison': couleur_saison,
            'mois_saison': ', '.join(mois_saison_list) if mois_saison_list else 'Toute l\'année',
            'nb_ingredients': recette.ingredients.count(),
            'score_pertinence': score_pertinence,
            'raisons': raisons,
            'est_recommandee': len(raisons) > 0,
            'nb_ingredients_communs': nb_communs
        })

    # Trier par pertinence décroissante
    resultats.sort(key=lambda x: x['score_pertinence'], reverse=True)

    # Limiter à 20 résultats
    return jsonify(resultats[:20])
