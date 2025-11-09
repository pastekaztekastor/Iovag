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


@bp.route('/complete-contextual-onboarding/<section>', methods=['POST'])
@login_required
def complete_contextual_onboarding(section):
    """Marquer l'onboarding contextuel comme complété pour une section"""
    if section == 'recettes':
        current_user.onboarding_recettes = True
    elif section == 'menus':
        current_user.onboarding_menus = True
    elif section == 'courses':
        current_user.onboarding_courses = True
    else:
        return {'error': 'Section invalide'}, 400

    db.session.commit()
    return {'success': True}, 200


@bp.route('/explore')
def explore_recipes():
    """Page pour explorer toutes les recettes publiques de la communauté"""
    # Récupérer toutes les recettes publiques
    recettes = Recette.query.filter_by(is_public=True)\
        .order_by(Recette.evaluation.desc(), Recette.created_at.desc()).all()

    return render_template('explore_recipes.html', recettes=recettes)


@bp.route('/profile')
@login_required
def profile():
    """Page de profil utilisateur"""
    from app.models import Stock

    # Statistiques de l'utilisateur
    nb_recettes = Recette.query.filter_by(created_by=current_user.id).count()
    nb_menus = Menu.query.filter_by(created_by=current_user.id).count()
    nb_stock = Stock.query.filter_by(user_id=current_user.id).count()
    nb_recettes_sauvegardees = current_user.recettes_sauvegardees.count()

    return render_template('profile.html',
                         nb_recettes=nb_recettes,
                         nb_menus=nb_menus,
                         nb_stock=nb_stock,
                         nb_recettes_sauvegardees=nb_recettes_sauvegardees)


@bp.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """Mettre à jour les informations du profil"""
    from app.models import User

    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()

    if not username or not email:
        flash('Le nom d\'utilisateur et l\'email sont obligatoires', 'danger')
        return redirect(url_for('main.profile'))

    # Vérifier si le username est déjà pris par un autre utilisateur
    if username != current_user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris', 'danger')
            return redirect(url_for('main.profile'))

    # Vérifier si l'email est déjà pris par un autre utilisateur
    if email != current_user.email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return redirect(url_for('main.profile'))

    current_user.username = username
    current_user.email = email
    db.session.commit()

    flash('Votre profil a été mis à jour avec succès', 'success')
    return redirect(url_for('main.profile'))


@bp.route('/profile/change-password', methods=['POST'])
@login_required
def profile_change_password():
    """Changer le mot de passe"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not all([current_password, new_password, confirm_password]):
        flash('Tous les champs sont obligatoires', 'danger')
        return redirect(url_for('main.profile'))

    # Vérifier le mot de passe actuel
    if not current_user.check_password(current_password):
        flash('Mot de passe actuel incorrect', 'danger')
        return redirect(url_for('main.profile'))

    # Vérifier que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas', 'danger')
        return redirect(url_for('main.profile'))

    # Vérifier la longueur du nouveau mot de passe
    if len(new_password) < 6:
        flash('Le nouveau mot de passe doit contenir au moins 6 caractères', 'danger')
        return redirect(url_for('main.profile'))

    current_user.set_password(new_password)
    db.session.commit()

    flash('Votre mot de passe a été changé avec succès', 'success')
    return redirect(url_for('main.profile'))


@bp.route('/profile/delete', methods=['POST'])
@login_required
def profile_delete():
    """Supprimer le compte utilisateur"""
    from flask_login import logout_user

    password = request.form.get('password', '')

    if not password:
        flash('Veuillez entrer votre mot de passe pour confirmer', 'danger')
        return redirect(url_for('main.profile'))

    # Vérifier le mot de passe
    if not current_user.check_password(password):
        flash('Mot de passe incorrect', 'danger')
        return redirect(url_for('main.profile'))

    # Supprimer l'utilisateur (cascade supprimera automatiquement ses données)
    user_to_delete = current_user
    logout_user()
    db.session.delete(user_to_delete)
    db.session.commit()

    flash('Votre compte a été supprimé avec succès', 'info')
    return redirect(url_for('main.index'))


@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Page de gestion des utilisateurs (admin seulement)"""
    from app.models import User, Stock

    users = User.query.order_by(User.created_at.desc()).all()

    # Calculer les statistiques pour chaque utilisateur
    users_stats = []
    for user in users:
        nb_recettes = Recette.query.filter_by(created_by=user.id).count()
        nb_menus = Menu.query.filter_by(created_by=user.id).count()
        nb_stock = Stock.query.filter_by(user_id=user.id).count()

        users_stats.append({
            'user': user,
            'nb_recettes': nb_recettes,
            'nb_menus': nb_menus,
            'nb_stock': nb_stock
        })

    return render_template('admin/users.html', users_stats=users_stats)


@bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    """Promouvoir/rétrograder un utilisateur en admin"""
    from app.models import User

    user = User.query.get_or_404(user_id)

    # Ne pas permettre de se rétrograder soi-même
    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre statut d\'administrateur', 'danger')
        return redirect(url_for('main.admin_users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    if user.is_admin:
        flash(f'{user.username} est maintenant administrateur', 'success')
    else:
        flash(f'{user.username} n\'est plus administrateur', 'success')

    return redirect(url_for('main.admin_users'))


@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Supprimer un utilisateur (admin seulement)"""
    from app.models import User

    user = User.query.get_or_404(user_id)

    # Ne pas permettre de se supprimer soi-même
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte via cette interface', 'danger')
        return redirect(url_for('main.admin_users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'L\'utilisateur {username} a été supprimé avec succès', 'success')
    return redirect(url_for('main.admin_users'))


@bp.route('/admin/comments')
@login_required
@admin_required
def admin_comments():
    """Page de gestion des commentaires (admin seulement)"""
    from app.models import RecetteCommentaire

    commentaires = RecetteCommentaire.query.order_by(RecetteCommentaire.created_at.desc()).all()

    return render_template('admin/comments.html', commentaires=commentaires)


@bp.route('/admin/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_comment(comment_id):
    """Supprimer un commentaire (admin seulement)"""
    from app.models import RecetteCommentaire

    commentaire = RecetteCommentaire.query.get_or_404(comment_id)

    recette_nom = commentaire.recette.nom
    user_nom = commentaire.utilisateur.username

    db.session.delete(commentaire)
    db.session.commit()

    flash(f'Commentaire de {user_nom} sur "{recette_nom}" supprimé avec succès', 'success')
    return redirect(url_for('main.admin_comments'))


@bp.route('/my-activity')
@login_required
def my_activity():
    """Page d'activité : recettes reprises et commentaires reçus"""
    from app.models import RecetteCommentaire, User

    # Mes recettes
    mes_recettes = Recette.query.filter_by(created_by=current_user.id).all()
    mes_recettes_ids = [r.id for r in mes_recettes]

    # Utilisateurs qui ont sauvegardé mes recettes
    recettes_reprises = []
    for recette in mes_recettes:
        nb_sauvegardes = recette.utilisateurs_sauvegardes.count()
        if nb_sauvegardes > 0:
            utilisateurs = recette.utilisateurs_sauvegardes.all()
            recettes_reprises.append({
                'recette': recette,
                'nb_sauvegardes': nb_sauvegardes,
                'utilisateurs': utilisateurs
            })

    # Trier par nombre de sauvegardes (décroissant)
    recettes_reprises.sort(key=lambda x: x['nb_sauvegardes'], reverse=True)

    # Commentaires reçus sur mes recettes
    commentaires_recus = RecetteCommentaire.query\
        .filter(RecetteCommentaire.recette_id.in_(mes_recettes_ids))\
        .filter(RecetteCommentaire.user_id != current_user.id)\
        .order_by(RecetteCommentaire.created_at.desc())\
        .all()

    return render_template('my_activity.html',
                         recettes_reprises=recettes_reprises,
                         commentaires_recus=commentaires_recus)
