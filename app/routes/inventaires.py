"""
Routes pour la gestion des inventaires
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Inventaire, InventaireItem, Ingredient, Stock
from collections import defaultdict

bp = Blueprint('inventaires', __name__, url_prefix='/inventaires')


@bp.route('/')
@login_required
def index():
    """Liste des inventaires"""
    inventaires = Inventaire.query.filter_by(created_by=current_user.id)\
        .order_by(Inventaire.date_inventaire.desc()).all()
    return render_template('inventaires/index.html', inventaires=inventaires)


@bp.route('/nouveau')
@login_required
def nouveau():
    """Formulaire de saisie d'un nouvel inventaire"""
    # Récupérer tous les stocks de l'utilisateur
    stocks = Stock.query.filter_by(user_id=current_user.id).all()

    # Grouper les stocks par lieu de rangement
    stocks_par_lieu = defaultdict(list)
    for stock in stocks:
        lieu = stock.ingredient.lieu_rangement or 'Non défini'
        stocks_par_lieu[lieu].append(stock)

    # Trier les lieux selon l'ordre prédéfini
    lieux_ordre = Ingredient.LIEUX_RANGEMENT + ['Non défini']
    stocks_ordonnes = {}
    for lieu in lieux_ordre:
        if lieu in stocks_par_lieu:
            # Trier les stocks par nom d'ingrédient dans chaque lieu
            stocks_ordonnes[lieu] = sorted(stocks_par_lieu[lieu], key=lambda s: s.ingredient.nom)

    return render_template('inventaires/nouveau.html', stocks_par_lieu=stocks_ordonnes)


@bp.route('/sauvegarder', methods=['POST'])
@login_required
def sauvegarder():
    """Sauvegarder un inventaire et mettre à jour les stocks"""
    notes = request.form.get('notes', '').strip()

    # Créer l'inventaire
    inventaire = Inventaire(
        created_by=current_user.id,
        notes=notes if notes else None
    )
    db.session.add(inventaire)
    db.session.flush()  # Pour obtenir l'ID

    # Parcourir tous les champs de quantité réelle
    nb_updates = 0
    nb_ecarts_negatifs = 0
    nb_ecarts_positifs = 0

    for key, value in request.form.items():
        if key.startswith('quantite_reelle_'):
            # Extraire l'ID du stock
            stock_id = int(key.replace('quantite_reelle_', ''))
            stock = Stock.query.get(stock_id)

            if not stock or stock.user_id != current_user.id:
                continue

            try:
                quantite_reelle = float(value) if value else 0
            except ValueError:
                quantite_reelle = 0

            quantite_theorique = stock.quantite
            ecart = quantite_reelle - quantite_theorique

            # Créer l'item d'inventaire
            item = InventaireItem(
                inventaire_id=inventaire.id,
                ingredient_id=stock.ingredient_id,
                quantite_theorique=quantite_theorique,
                quantite_reelle=quantite_reelle,
                ecart=ecart,
                unite=stock.unite
            )
            db.session.add(item)

            # Mettre à jour le stock si différent
            if ecart != 0:
                stock.quantite = quantite_reelle
                nb_updates += 1

                if ecart < 0:
                    nb_ecarts_negatifs += 1
                else:
                    nb_ecarts_positifs += 1

    db.session.commit()

    # Message de succès avec résumé
    message = f'Inventaire enregistré avec succès'
    if nb_updates > 0:
        message += f' - {nb_updates} ingrédient(s) mis à jour'
        if nb_ecarts_negatifs > 0:
            message += f' ({nb_ecarts_negatifs} manquant(s)'
        if nb_ecarts_positifs > 0:
            if nb_ecarts_negatifs > 0:
                message += f', {nb_ecarts_positifs} en surplus)'
            else:
                message += f' ({nb_ecarts_positifs} en surplus)'
        elif nb_ecarts_negatifs > 0:
            message += ')'

    flash(message, 'success')
    return redirect(url_for('inventaires.detail', id=inventaire.id))


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'un inventaire"""
    inventaire = Inventaire.query.get_or_404(id)

    if inventaire.created_by != current_user.id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('inventaires.index'))

    # Grouper les items par lieu de rangement
    items_par_lieu = defaultdict(list)
    for item in inventaire.items:
        lieu = item.ingredient.lieu_rangement or 'Non défini'
        items_par_lieu[lieu].append(item)

    # Trier les lieux selon l'ordre prédéfini
    lieux_ordre = Ingredient.LIEUX_RANGEMENT + ['Non défini']
    items_ordonnes = {}
    for lieu in lieux_ordre:
        if lieu in items_par_lieu:
            # Trier les items par nom d'ingrédient dans chaque lieu
            items_ordonnes[lieu] = sorted(items_par_lieu[lieu], key=lambda i: i.ingredient.nom)

    return render_template('inventaires/detail.html',
                          inventaire=inventaire,
                          items_par_lieu=items_ordonnes)


@bp.route('/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer(id):
    """Supprimer un inventaire"""
    inventaire = Inventaire.query.get_or_404(id)

    if inventaire.created_by != current_user.id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('inventaires.index'))

    db.session.delete(inventaire)
    db.session.commit()

    flash('Inventaire supprimé avec succès', 'success')
    return redirect(url_for('inventaires.index'))
