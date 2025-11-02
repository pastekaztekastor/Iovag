"""
Routes pour la gestion du stock
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Stock, Ingredient
from sqlalchemy import func

bp = Blueprint('stock', __name__, url_prefix='/stock')

# Seuils de stock bas par défaut par catégorie (utilisés si stock_limite n'est pas défini)
SEUILS_STOCK_BAS_DEFAUT = {
    'Fruits & Légumes': 200,  # grammes
    'Viandes & Poissons': 200,
    'Produits laitiers': 100,
    'Épicerie salée': 100,
    'Épicerie sucrée': 100,
    'Surgelés': 200,
    'Boissons': 250,  # ml
    'Pain & Viennoiseries': 1,
    'Condiments & Sauces': 50,
    'Herbes & Épices': 10,
    'Conserves': 1,
    'Pâtes & Riz': 200,
    'Huiles & Vinaigres': 100,
    'Autre': 50
}


def est_stock_bas(stock_item):
    """
    Déterminer si un item de stock est bas
    Utilise en priorité le stock_limite de l'ingrédient,
    sinon utilise les seuils par défaut selon la catégorie
    """
    # Utiliser stock_limite si défini
    if stock_item.ingredient.stock_limite is not None:
        return stock_item.quantite <= stock_item.ingredient.stock_limite

    # Sinon utiliser le seuil par défaut de la catégorie
    if not stock_item.ingredient.categorie:
        seuil = SEUILS_STOCK_BAS_DEFAUT.get('Autre', 50)
    else:
        seuil = SEUILS_STOCK_BAS_DEFAUT.get(stock_item.ingredient.categorie, 50)

    return stock_item.quantite <= seuil


@bp.route('/')
@login_required
def index():
    """Liste du stock avec filtres"""
    # Récupérer tous les stocks de l'utilisateur
    stocks = Stock.query.filter_by(user_id=current_user.id)\
        .join(Ingredient)\
        .order_by(Ingredient.nom)\
        .all()

    # Compter les stocks bas
    nb_stock_bas = sum(1 for s in stocks if est_stock_bas(s))

    return render_template('stock/index.html',
                         stocks=stocks,
                         nb_stock_bas=nb_stock_bas,
                         lieux_rangement=Ingredient.LIEUX_RANGEMENT)


@bp.route('/par-lieu')
@login_required
def par_lieu():
    """Vue du stock organisée par lieu de rangement"""
    # Récupérer tous les stocks avec leurs ingrédients
    stocks = Stock.query.filter_by(user_id=current_user.id)\
        .join(Ingredient)\
        .order_by(Ingredient.lieu_rangement, Ingredient.nom)\
        .all()

    # Organiser par lieu de rangement
    stock_par_lieu = {}
    for stock in stocks:
        lieu = stock.ingredient.lieu_rangement or 'Non défini'
        if lieu not in stock_par_lieu:
            stock_par_lieu[lieu] = []
        stock_par_lieu[lieu].append(stock)

    # Compter les stocks bas
    nb_stock_bas = sum(1 for s in stocks if est_stock_bas(s))

    return render_template('stock/par_lieu.html',
                         stock_par_lieu=stock_par_lieu,
                         nb_stock_bas=nb_stock_bas,
                         lieux_rangement=Ingredient.LIEUX_RANGEMENT)


@bp.route('/adjust/<int:id>', methods=['POST'])
@login_required
def adjust(id):
    """Ajuster la quantité d'un stock (AJAX)"""
    stock = Stock.query.get_or_404(id)

    # Vérifier que le stock appartient à l'utilisateur
    if stock.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.get_json()
    action = data.get('action')  # 'increase' ou 'decrease' ou 'set'
    quantite = float(data.get('quantite', 0))
    raison = data.get('raison', '')

    if action == 'increase':
        stock.quantite += quantite
    elif action == 'decrease':
        stock.quantite = max(0, stock.quantite - quantite)
    elif action == 'set':
        stock.quantite = max(0, quantite)

    db.session.commit()

    return jsonify({
        'success': True,
        'nouvelle_quantite': stock.quantite,
        'stock_bas': est_stock_bas(stock)
    })


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Ajouter un ingrédient au stock manuellement"""
    if request.method == 'POST':
        ingredient_id = request.form.get('ingredient_id', type=int)
        quantite = request.form.get('quantite', type=float)
        unite = request.form.get('unite')
        raison = request.form.get('raison', 'Ajout manuel')

        if not ingredient_id or quantite is None or quantite <= 0:
            flash('Données invalides', 'danger')
            return redirect(url_for('stock.add'))

        # Vérifier si l'ingrédient existe déjà dans le stock
        stock_existant = Stock.query.filter_by(
            user_id=current_user.id,
            ingredient_id=ingredient_id
        ).first()

        if stock_existant:
            # Ajouter à la quantité existante
            stock_existant.quantite += quantite
            stock_existant.unite = unite
            flash(f'Stock mis à jour : +{quantite} {unite}', 'success')
        else:
            # Créer un nouveau stock
            nouveau_stock = Stock(
                user_id=current_user.id,
                ingredient_id=ingredient_id,
                quantite=quantite,
                unite=unite
            )
            db.session.add(nouveau_stock)
            flash('Ingrédient ajouté au stock', 'success')

        db.session.commit()
        return redirect(url_for('stock.index'))

    # GET - Afficher le formulaire
    ingredients = Ingredient.query.order_by(Ingredient.nom).all()
    return render_template('stock/add.html', ingredients=ingredients)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer un ingrédient du stock"""
    stock = Stock.query.get_or_404(id)

    # Vérifier que le stock appartient à l'utilisateur
    if stock.user_id != current_user.id:
        flash('Vous n\'avez pas la permission de supprimer cet élément', 'danger')
        return redirect(url_for('stock.index'))

    nom_ingredient = stock.ingredient.nom
    db.session.delete(stock)
    db.session.commit()

    flash(f'{nom_ingredient} retiré du stock', 'success')
    return redirect(url_for('stock.index'))


@bp.route('/nb-stock-bas')
@login_required
def nb_stock_bas():
    """Retourner le nombre d'articles en stock bas (pour le badge)"""
    stocks = Stock.query.filter_by(user_id=current_user.id)\
        .join(Ingredient)\
        .all()

    nb = sum(1 for s in stocks if est_stock_bas(s))
    return jsonify({'nb_stock_bas': nb})
