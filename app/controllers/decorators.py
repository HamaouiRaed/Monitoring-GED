from functools import wraps
from flask import session, redirect, url_for, flash

# ✅ Protection réservée aux admins
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for('main.unauthorized'))
        return f(*args, **kwargs)
    return decorated_function

# ✅ Protection générale : requiert une session valide
def login_required_custom(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            flash("Session expirée ou utilisateur déconnecté.", "warning")
            return redirect(url_for("login.login_page"))  # ✅ route GET
        return f(*args, **kwargs)
    return decorated_function
