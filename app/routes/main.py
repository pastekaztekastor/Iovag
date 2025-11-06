"""
Routes principales de l'application
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import Menu, Recette, ContactMessage
from app import db
from app.decorators import admin_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        # Vérifier si l'utilisateur doit voir l'onboarding
        if not current_user.onboarding_completed:
            return redirect(url_for('main.onboarding'))

        # Récupérer les menus et recettes récents de l'utilisateur
        menus_recents = Menu.query.filter_by(created_by=current_user.id)\
            .order_by(Menu.created_at.desc()).limit(6).all()
        recettes_favorites = Recette.query.filter_by(created_by=current_user.id)\
            .filter(Recette.evaluation >= 4)\
            .order_by(Recette.evaluation.desc()).limit(6).all()

        return render_template('index.html',
                             menus_recents=menus_recents,
                             recettes_favorites=recettes_favorites)
    else:
        # Récupérer les meilleures recettes publiques pour les visiteurs
        top_recettes = Recette.query.filter_by(is_public=True)\
            .filter(Recette.evaluation >= 4)\
            .order_by(Recette.evaluation.desc(), Recette.created_at.desc())\
            .limit(10).all()
        return render_template('landing.html', top_recettes=top_recettes)


@bp.route('/about')
def about():
    """Page Qui sommes-nous"""
    return render_template('about.html')


@bp.route('/faq')
def faq():
    """Page FAQ"""
    return render_template('faq.html')


@bp.route('/cgu')
def cgu():
    """Page CGU (Conditions Générales d'Utilisation)"""
    from datetime import datetime
    return render_template('cgu.html', date=datetime.now().strftime('%d/%m/%Y'))


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Page Contact"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Validation
        if not all([name, email, subject, message]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return redirect(url_for('main.contact'))

        # Créer le message de contact
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(contact_msg)
        db.session.commit()

        flash('Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')


@bp.route('/admin/contact-messages')
@login_required
@admin_required
def admin_contact_messages():
    """Page admin pour consulter les messages de contact"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contact_messages.html', messages=messages)


@bp.route('/admin/contact-messages/<int:message_id>/mark-read', methods=['POST'])
@login_required
@admin_required
def mark_message_read(message_id):
    """Marquer un message comme lu"""
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    flash('Message marqué comme lu.', 'success')
    return redirect(url_for('main.admin_contact_messages'))


@bp.route('/admin/contact-messages/<int:message_id>/mark-replied', methods=['POST'])
@login_required
@admin_required
def mark_message_replied(message_id):
    """Marquer un message comme répondu"""
    message = ContactMessage.query.get_or_404(message_id)
    message.replied = True
    db.session.commit()
    flash('Message marqué comme répondu.', 'success')
    return redirect(url_for('main.admin_contact_messages'))


@bp.route('/admin/contact-messages/<int:message_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_contact_message(message_id):
    """Supprimer un message de contact"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message supprimé.', 'success')
    return redirect(url_for('main.admin_contact_messages'))


@bp.route('/onboarding')
@login_required
def onboarding():
    """Page d'onboarding pour les nouveaux utilisateurs"""
    # Si l'utilisateur a déjà complété l'onboarding, le rediriger
    if current_user.onboarding_completed:
        return redirect(url_for('main.index'))
    return render_template('onboarding.html')


@bp.route('/complete-onboarding', methods=['POST'])
@login_required
def complete_onboarding():
    """Marquer l'onboarding comme complété"""
    current_user.onboarding_completed = True
    db.session.commit()
    flash('Bienvenue sur Iovag ! Vous êtes prêt à commencer.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/explore')
def explore_recipes():
    """Page pour explorer toutes les recettes publiques de la communauté"""
    # Récupérer toutes les recettes publiques
    recettes = Recette.query.filter_by(is_public=True)\
        .order_by(Recette.evaluation.desc(), Recette.created_at.desc()).all()

    return render_template('explore_recipes.html', recettes=recettes)
