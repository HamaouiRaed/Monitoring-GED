from flask import Blueprint, session, redirect, url_for, jsonify
from flask_login import logout_user as flask_logout_user
from flask_jwt_extended import unset_jwt_cookies

logout = Blueprint("logout", __name__)

@logout.route('/logout', methods=['POST', 'GET'])
def logout_user():
    # ✅ Déconnexion Flask-Login
    flask_logout_user()

    # 🧹 Nettoyage de la session
    session.clear()

    # ❌ Supprimer le cookie JWT
    response = jsonify({"message": "Déconnexion réussie."})
    unset_jwt_cookies(response)

    return response, 200
