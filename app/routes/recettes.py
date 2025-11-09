"""
Routes pour la gestion des recettes
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Recette, Ingredient, RecetteIngredient, Instruction, RecetteCommentaire

bp = Blueprint('recettes', __name__, url_prefix='/recettes')


@bp.route('/')
@login_required
def index():
    """Liste des recettes"""
    from datetime import datetime
    recettes = Recette.query.filter_by(created_by=current_user.id).all()
    return render_template('recettes/index.html', recettes=recettes, now=datetime.now())


@bp.route('/saved')
@login_required
def saved():
    """Liste des recettes sauvegardées (des autres utilisateurs)"""
    from datetime import datetime
    recettes_sauvegardees = current_user.recettes_sauvegardees.all()
    return render_template('recettes/saved.html', recettes=recettes_sauvegardees, now=datetime.now())


@bp.route('/possibles')
@login_required
def possibles():
    """Liste des recettes possibles avec le stock actuel"""
    from app.models import Stock, UnitConverter
    import math

    # Récupérer toutes les recettes de l'utilisateur
    recettes = Recette.query.filter_by(created_by=current_user.id).all()

    recettes_possibles = []

    for recette in recettes:
        # Calculer combien de fois on peut faire cette recette
        ratio_min = float('inf')
        ingredients_manquants = []
        tous_ingredients_disponibles = True

        for ri in recette.ingredients:
            # Chercher le stock pour cet ingrédient
            stock_item = Stock.query.filter_by(
                user_id=current_user.id,
                ingredient_id=ri.ingredient.id
            ).first()

            if not stock_item or stock_item.quantite <= 0:
                tous_ingredients_disponibles = False
                ingredients_manquants.append(ri.ingredient.nom)
                ratio_min = 0
            else:
                # Normaliser les unités pour comparer
                stock_normalise, stock_unite = UnitConverter.normaliser(
                    stock_item.quantite, stock_item.unite, ri.ingredient
                )
                ingredient_normalise, ingredient_unite = UnitConverter.normaliser(
                    ri.quantite, ri.unite, ri.ingredient
                )

                # Si les unités sont compatibles
                if stock_unite == ingredient_unite:
                    # Calculer combien de fois on peut faire la recette avec cet ingrédient
                    ratio = stock_normalise / ingredient_normalise
                    ratio_min = min(ratio_min, ratio)
                else:
                    # Unités incompatibles
                    tous_ingredients_disponibles = False
                    ingredients_manquants.append(ri.ingredient.nom)
                    ratio_min = 0

        # Si ratio_min est toujours infini, la recette n'a pas d'ingrédients
        if ratio_min == float('inf'):
            ratio_min = 0

        # Calculer le nombre de portions max (arrondi à l'entier inférieur)
        portions_max = int(math.floor(ratio_min * recette.portions))

        # Ajouter à la liste si on peut faire au moins 1 portion
        if portions_max > 0:
            recettes_possibles.append({
                'recette': recette,
                'portions_max': portions_max,
                'ratio': ratio_min,
                'tous_ingredients': tous_ingredients_disponibles
            })

    # Trier par nombre de portions max (décroissant)
    recettes_possibles.sort(key=lambda x: x['portions_max'], reverse=True)

    return render_template('recettes/possibles.html', recettes_possibles=recettes_possibles)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'une recette"""
    from app.models import Stock, UnitConverter

    recette = Recette.query.get_or_404(id)

    # Calculer le stock disponible pour chaque ingrédient
    stock_info = {}
    for ri in recette.ingredients:
        stock_item = Stock.query.filter_by(
            user_id=current_user.id,
            ingredient_id=ri.ingredient.id
        ).first()

        if stock_item and stock_item.quantite > 0:
            # Normaliser pour comparer
            stock_normalise, stock_unite = UnitConverter.normaliser(
                stock_item.quantite, stock_item.unite, ri.ingredient
            )
            ingredient_normalise, ingredient_unite = UnitConverter.normaliser(
                ri.quantite, ri.unite, ri.ingredient
            )

            # Vérifier si on a assez en stock
            if stock_unite == ingredient_unite:
                en_stock = stock_normalise >= ingredient_normalise
                stock_info[ri.id] = {
                    'en_stock': en_stock,
                    'quantite_stock': stock_item.quantite,
                    'unite_stock': stock_item.unite
                }
            else:
                stock_info[ri.id] = {'en_stock': False, 'quantite_stock': 0, 'unite_stock': ''}
        else:
            stock_info[ri.id] = {'en_stock': False, 'quantite_stock': 0, 'unite_stock': ''}

    return render_template('recettes/detail.html', recette=recette, stock_info=stock_info)


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

        # Récupérer la visibilité
        is_public = 'is_public' in request.form

        # Récupérer les paramètres de divisibilité
        est_divisible = 'est_divisible' in request.form
        portions_min = request.form.get('portions_min', type=int)

        # Créer la recette
        recette = Recette(
            nom=nom,
            portions=portions,
            portions_min=portions_min if portions_min else None,
            est_divisible=est_divisible,
            temps_preparation=temps_preparation if temps_preparation else None,
            temps_cuisson=temps_cuisson if temps_cuisson else None,
            auteur_nom=auteur_nom if auteur_nom else None,
            evaluation=evaluation,
            note=note if note else None,
            mois_saison=mois_saison_str,
            type_repas=type_repas_str,
            is_public=is_public,
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

        # Mettre à jour la visibilité
        recette.is_public = 'is_public' in request.form

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


@bp.route('/<int:id>/save', methods=['POST'])
@login_required
def save_recipe(id):
    """Ajouter une recette publique à ses favoris"""
    recette = Recette.query.get_or_404(id)

    # Vérifier que la recette est publique
    if not recette.is_public and recette.created_by != current_user.id:
        flash('Cette recette n\'est pas disponible.', 'danger')
        return redirect(url_for('main.explore_recipes'))

    # Vérifier que l'utilisateur ne sauvegarde pas sa propre recette
    if recette.created_by == current_user.id:
        flash('Cette recette vous appartient déjà.', 'info')
        return redirect(url_for('recettes.detail', id=id))

    # Vérifier si déjà sauvegardée
    if recette in current_user.recettes_sauvegardees:
        flash('Cette recette est déjà dans votre catalogue.', 'info')
        return redirect(url_for('recettes.detail', id=id))

    # Ajouter aux favoris
    current_user.recettes_sauvegardees.append(recette)
    db.session.commit()
    flash(f'Recette "{recette.nom}" ajoutée à votre catalogue !', 'success')
    return redirect(url_for('recettes.detail', id=id))


@bp.route('/<int:id>/unsave', methods=['POST'])
@login_required
def unsave_recipe(id):
    """Retirer une recette de ses favoris"""
    recette = Recette.query.get_or_404(id)

    if recette not in current_user.recettes_sauvegardees:
        flash('Cette recette n\'est pas dans votre catalogue.', 'info')
        return redirect(url_for('recettes.detail', id=id))

    current_user.recettes_sauvegardees.remove(recette)
    db.session.commit()
    flash(f'Recette "{recette.nom}" retirée de votre catalogue.', 'success')
    return redirect(url_for('recettes.saved'))


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

    # Récupérer toutes les recettes de l'utilisateur + recettes sauvegardées
    recettes_perso = Recette.query.filter_by(created_by=current_user.id).all()
    recettes_sauvegardees = current_user.recettes_sauvegardees.all()
    recettes = recettes_perso + recettes_sauvegardees

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


@bp.route('/<int:id>/commentaire', methods=['POST'])
@login_required
def ajouter_commentaire(id):
    """Ajouter ou modifier son commentaire sur une recette"""
    from app.models import RecetteCommentaire
    
    recette = Recette.query.get_or_404(id)
    commentaire_texte = request.form.get('commentaire', '').strip()
    
    if not commentaire_texte:
        flash('Le commentaire ne peut pas être vide', 'error')
        return redirect(url_for('recettes.detail', id=id))
    
    # Chercher si l'utilisateur a déjà un commentaire
    commentaire = RecetteCommentaire.query.filter_by(
        recette_id=id,
        user_id=current_user.id
    ).first()
    
    if commentaire:
        # Modifier le commentaire existant
        commentaire.commentaire = commentaire_texte
        commentaire.updated_at = datetime.utcnow()
        flash('Votre commentaire a été modifié', 'success')
    else:
        # Créer un nouveau commentaire
        commentaire = RecetteCommentaire(
            recette_id=id,
            user_id=current_user.id,
            commentaire=commentaire_texte
        )
        db.session.add(commentaire)
        flash('Votre commentaire a été ajouté', 'success')
    
    db.session.commit()
    return redirect(url_for('recettes.detail', id=id))


@bp.route('/<int:id>/commentaire/supprimer', methods=['POST'])
@login_required
def supprimer_commentaire(id):
    """Supprimer son commentaire"""
    from app.models import RecetteCommentaire
    
    commentaire = RecetteCommentaire.query.filter_by(
        recette_id=id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(commentaire)
    db.session.commit()
    flash('Votre commentaire a été supprimé', 'success')
    return redirect(url_for('recettes.detail', id=id))


@bp.route('/<int:recette_id>/commentaire/<int:comment_id>/repondre', methods=['POST'])
@login_required
def repondre_commentaire(recette_id, comment_id):
    """Répondre à un commentaire (auteur de la recette seulement)"""
    from app.models import RecetteCommentaire
    
    recette = Recette.query.get_or_404(recette_id)
    
    # Vérifier que l'utilisateur est l'auteur de la recette
    if recette.created_by != current_user.id:
        flash('Vous n\'êtes pas autorisé à répondre à ce commentaire', 'error')
        return redirect(url_for('recettes.detail', id=recette_id))
    
    commentaire = RecetteCommentaire.query.get_or_404(comment_id)
    reponse = request.form.get('reponse', '').strip()
    
    if reponse:
        commentaire.reponse_auteur = reponse
        commentaire.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Votre réponse a été ajoutée', 'success')
    else:
        flash('La réponse ne peut pas être vide', 'error')
    
    return redirect(url_for('recettes.detail', id=recette_id))


@bp.route('/<int:id>/cuisiner', methods=['POST'])
@login_required
def cuisiner(id):
    """Retirer les ingrédients de la recette du stock"""
    from app.models import Stock

    recette = Recette.query.get_or_404(id)
    nb_personnes = request.form.get('nb_personnes', type=int, default=recette.portions)

    # Valider le nombre de portions
    est_valide, message, portions_min = recette.valider_portions(nb_personnes)
    if not est_valide:
        flash(message, 'danger')
        return redirect(url_for('recettes.detail', id=id))

    # Pour chaque ingrédient de la recette
    ingredients_retires = []
    ingredients_manquants = []

    for ri in recette.ingredients:
        # Calculer la quantité nécessaire
        ratio = nb_personnes / recette.portions
        quantite_necessaire = ri.quantite * ratio

        # Chercher le stock de l'utilisateur
        stock_item = Stock.query.filter_by(
            user_id=current_user.id,
            ingredient_id=ri.ingredient.id
        ).first()

        if stock_item and stock_item.quantite > 0:
            # Ne pas créer de stock négatif
            quantite_retiree = min(stock_item.quantite, quantite_necessaire)
            stock_item.quantite -= quantite_retiree

            if stock_item.quantite <= 0:
                db.session.delete(stock_item)

            ingredients_retires.append(ri.ingredient.nom)

            # Si on n'a pas pu retirer toute la quantité nécessaire
            if quantite_retiree < quantite_necessaire:
                ingredients_manquants.append(ri.ingredient.nom)
        else:
            # Pas de stock pour cet ingrédient
            ingredients_manquants.append(ri.ingredient.nom)

    db.session.commit()

    # Messages de retour
    if ingredients_manquants:
        flash(f'Stock mis à jour pour {nb_personnes} portions. Attention : {len(ingredients_manquants)} ingrédient(s) manquant(s) ou insuffisant(s).', 'warning')
    else:
        flash(f'Ingrédients retirés du stock pour {nb_personnes} portions', 'success')

    return redirect(url_for('recettes.detail', id=id))


@bp.route('/<int:id>/pdf')
@login_required
def telecharger_pdf(id):
    """Télécharger une recette en PDF"""
    from flask import send_file
    from app.pdf_generator import generer_pdf_recette

    recette = Recette.query.get_or_404(id)

    # Vérifier les permissions
    if not recette.is_public and recette.created_by != current_user.id:
        flash('Vous n\'avez pas accès à cette recette', 'danger')
        return redirect(url_for('recettes.index'))

    # Nombre de portions depuis les paramètres GET (optionnel)
    portions = request.args.get('portions', type=int)

    # Générer le PDF
    pdf_buffer = generer_pdf_recette(recette, portions)

    # Nom du fichier
    filename = f"recette_{recette.nom.replace(' ', '_')}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/<int:id>/texte')
@login_required
def format_texte(id):
    """Retourne la recette au format texte pour copie dans le presse-papier"""
    recette = Recette.query.get_or_404(id)

    # Vérifier les permissions
    if not recette.is_public and recette.created_by != current_user.id:
        return jsonify({'error': 'Accès refusé'}), 403

    # Nombre de portions depuis les paramètres GET (optionnel)
    portions = request.args.get('portions', type=int) or recette.portions_min or 1

    # Construire le texte
    texte = f"{recette.nom}\n"
    texte += "=" * len(recette.nom) + "\n\n"

    texte += f"Portions: {portions}\n"
    if recette.temps_preparation:
        texte += f"Temps de préparation: {recette.temps_preparation} min\n"
    if recette.evaluation:
        texte += f"Évaluation: {recette.evaluation}/5\n"
    texte += "\n"

    # Ingrédients
    texte += "INGRÉDIENTS:\n"
    texte += "-" * 40 + "\n"

    for ri in recette.recette_ingredients.all():
        # Ajuster les quantités selon le nombre de portions
        quantite_base = ri.quantite
        if portions and recette.portions_min:
            ratio = portions / recette.portions_min
            quantite_affichee = round(quantite_base * ratio, 2)
        else:
            quantite_affichee = quantite_base

        texte += f"• {ri.ingredient.nom}: {quantite_affichee} {ri.unite or 'g'}\n"

    texte += "\n"

    # Instructions
    texte += "INSTRUCTIONS:\n"
    texte += "-" * 40 + "\n"

    if recette.instructions:
        instructions_lines = recette.instructions.split('\n')
        for i, line in enumerate(instructions_lines, 1):
            if line.strip():
                texte += f"{i}. {line.strip()}\n"
    else:
        texte += "Aucune instruction définie\n"

    texte += "\n"

    # Notes
    if recette.notes:
        texte += "NOTES:\n"
        texte += "-" * 40 + "\n"
        texte += recette.notes + "\n"

    return jsonify({'texte': texte})
