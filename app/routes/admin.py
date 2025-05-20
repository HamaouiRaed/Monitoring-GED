from flask import Blueprint, render_template, session, redirect, url_for, make_response
from flask_login import login_required

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def admin_dashboard():
    # ✅ Vérifie que l'utilisateur est bien admin
    if session.get("role") != "admin":
        return redirect(url_for("main.unauthorized"))
    user = {
        "username": session.get("username"),
        "role": session.get("role")
    }

    # ✅ Empêche le navigateur de mettre la page en cache
    response = make_response(render_template("dashboard.html", user=user))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
