"""
Routes pour la gestion des unités et conversions
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Unite, IngredientConversionUnite, Ingredient
from app.decorators import admin_required

bp = Blueprint('unites', __name__, url_prefix='/unites')


@bp.route('/')
@login_required
@admin_required
def index():
    """Liste de toutes les unités"""
    unites_masse = Unite.query.filter_by(type_unite='masse').order_by(Unite.nom).all()
    unites_volume = Unite.query.filter_by(type_unite='volume').order_by(Unite.nom).all()
    unites_unitaires = Unite.query.filter_by(type_unite='unitaire').order_by(Unite.nom).all()

    return render_template('admin/unites.html',
                         unites_masse=unites_masse,
                         unites_volume=unites_volume,
                         unites_unitaires=unites_unitaires)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Créer une nouvelle unité"""
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        symbole = request.form.get('symbole', '').strip()
        type_unite = request.form.get('type_unite')
        facteur_vers_base = request.form.get('facteur_vers_base', type=float)
        unite_base_id = request.form.get('unite_base_id', type=int)
        description = request.form.get('description', '').strip()

        if not all([nom, symbole, type_unite]):
            flash('Le nom, le symbole et le type sont obligatoires', 'danger')
            return redirect(url_for('unites.create'))

        # Vérifier que l'unité n'existe pas déjà
        if Unite.query.filter_by(nom=nom).first():
            flash(f'L\'unité "{nom}" existe déjà', 'danger')
            return redirect(url_for('unites.create'))

        nouvelle_unite = Unite(
            nom=nom,
            symbole=symbole,
            type_unite=type_unite,
            facteur_vers_base=facteur_vers_base or 1.0,
            unite_base_id=unite_base_id if unite_base_id else None,
            description=description if description else None
        )

        db.session.add(nouvelle_unite)
        db.session.commit()

        flash(f'Unité "{nom}" créée avec succès', 'success')
        return redirect(url_for('unites.index'))

    # GET - Afficher le formulaire
    unites_bases = Unite.query.filter(Unite.unite_base_id.is_(None)).all()
    return render_template('admin/unites_create.html', unites_bases=unites_bases)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Modifier une unité"""
    unite = Unite.query.get_or_404(id)

    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        symbole = request.form.get('symbole', '').strip()
        type_unite = request.form.get('type_unite')
        facteur_vers_base = request.form.get('facteur_vers_base', type=float)
        unite_base_id = request.form.get('unite_base_id', type=int)
        description = request.form.get('description', '').strip()

        if not all([nom, symbole, type_unite]):
            flash('Le nom, le symbole et le type sont obligatoires', 'danger')
            return redirect(url_for('unites.edit', id=id))

        # Vérifier que le nom n'est pas déjà pris par une autre unité
        existing = Unite.query.filter_by(nom=nom).first()
        if existing and existing.id != id:
            flash(f'L\'unité "{nom}" existe déjà', 'danger')
            return redirect(url_for('unites.edit', id=id))

        unite.nom = nom
        unite.symbole = symbole
        unite.type_unite = type_unite
        unite.facteur_vers_base = facteur_vers_base or 1.0
        unite.unite_base_id = unite_base_id if unite_base_id else None
        unite.description = description if description else None

        db.session.commit()

        flash(f'Unité "{nom}" modifiée avec succès', 'success')
        return redirect(url_for('unites.index'))

    # GET
    unites_bases = Unite.query.filter(Unite.unite_base_id.is_(None)).all()
    return render_template('admin/unites_edit.html', unite=unite, unites_bases=unites_bases)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Supprimer une unité"""
    unite = Unite.query.get_or_404(id)

    # Vérifier si d'autres unités dépendent de celle-ci
    unites_derivees = Unite.query.filter_by(unite_base_id=id).count()
    if unites_derivees > 0:
        flash(f'Impossible de supprimer "{unite.nom}" car {unites_derivees} unité(s) en dépendent', 'danger')
        return redirect(url_for('unites.index'))

    nom = unite.nom
    db.session.delete(unite)
    db.session.commit()

    flash(f'Unité "{nom}" supprimée avec succès', 'success')
    return redirect(url_for('unites.index'))


@bp.route('/conversions')
@login_required
@admin_required
def conversions():
    """Liste des conversions personnalisées par ingrédient"""
    conversions = IngredientConversionUnite.query\
        .join(Ingredient)\
        .order_by(Ingredient.nom).all()

    return render_template('admin/conversions.html', conversions=conversions)


@bp.route('/conversions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def conversion_create():
    """Créer une conversion personnalisée"""
    if request.method == 'POST':
        ingredient_id = request.form.get('ingredient_id', type=int)
        unite_source_id = request.form.get('unite_source_id', type=int)
        unite_cible_id = request.form.get('unite_cible_id', type=int)
        facteur_conversion = request.form.get('facteur_conversion', type=float)
        notes = request.form.get('notes', '').strip()

        if not all([ingredient_id, unite_source_id, unite_cible_id, facteur_conversion]):
            flash('Tous les champs sont obligatoires', 'danger')
            return redirect(url_for('unites.conversion_create'))

        # Vérifier que la conversion n'existe pas déjà
        existing = IngredientConversionUnite.query.filter_by(
            ingredient_id=ingredient_id,
            unite_source_id=unite_source_id,
            unite_cible_id=unite_cible_id
        ).first()

        if existing:
            flash('Cette conversion existe déjà', 'danger')
            return redirect(url_for('unites.conversion_create'))

        nouvelle_conversion = IngredientConversionUnite(
            ingredient_id=ingredient_id,
            unite_source_id=unite_source_id,
            unite_cible_id=unite_cible_id,
            facteur_conversion=facteur_conversion,
            notes=notes if notes else None
        )

        db.session.add(nouvelle_conversion)
        db.session.commit()

        flash('Conversion créée avec succès', 'success')
        return redirect(url_for('unites.conversions'))

    # GET
    ingredients = Ingredient.query.order_by(Ingredient.nom).all()
    unites = Unite.query.order_by(Unite.type_unite, Unite.nom).all()

    return render_template('admin/conversions_create.html',
                         ingredients=ingredients,
                         unites=unites)


@bp.route('/conversions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def conversion_edit(id):
    """Modifier une conversion"""
    conversion = IngredientConversionUnite.query.get_or_404(id)

    if request.method == 'POST':
        facteur_conversion = request.form.get('facteur_conversion', type=float)
        notes = request.form.get('notes', '').strip()

        if not facteur_conversion:
            flash('Le facteur de conversion est obligatoire', 'danger')
            return redirect(url_for('unites.conversion_edit', id=id))

        conversion.facteur_conversion = facteur_conversion
        conversion.notes = notes if notes else None

        db.session.commit()

        flash('Conversion modifiée avec succès', 'success')
        return redirect(url_for('unites.conversions'))

    # GET
    return render_template('admin/conversions_edit.html', conversion=conversion)


@bp.route('/conversions/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def conversion_delete(id):
    """Supprimer une conversion"""
    conversion = IngredientConversionUnite.query.get_or_404(id)

    db.session.delete(conversion)
    db.session.commit()

    flash('Conversion supprimée avec succès', 'success')
    return redirect(url_for('unites.conversions'))
