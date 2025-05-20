from flask import Blueprint, request, jsonify, session, render_template
from flask_login import login_user as flask_login_user
from app.models.user import User

login = Blueprint("login", __name__)

# ✅ Route GET : Affichage du formulaire HTML
@login.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html")

# ✅ Route POST : Traitement de la connexion
@login.route('/login', methods=['POST'])
def handle_login():
    try:
        # 🔍 Accepter JSON (frontend JS) ou form classique
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Nom d'utilisateur ou mot de passe manquant."}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Nom d'utilisateur ou mot de passe invalide."}), 401

        # ✅ Authentification Flask-Login
        flask_login_user(user)


        # ✅ Enregistrement session (si nécessaire pour autres logiques)
        session['username'] = user.username
        session['role'] = user.role
        session['user_id'] = user.id

        # ✅ Préparation de la réponse
        response = jsonify({
            "message": "Connexion réussie.",
            "redirect_url": "/dashboard" if user.role == "user" else "/admin",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        })

        return response, 200

    except Exception as e:
        print("Erreur serveur:", str(e))
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500
