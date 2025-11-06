"""
Décorateurs personnalisés pour l'application
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement
    Usage: @admin_required après @login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Accès refusé. Cette page est réservée aux administrateurs.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
