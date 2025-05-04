from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app import db
from app.models.user import User

login = Blueprint("login", __name__)

# Login route to authenticate user and store user information in the session
@login.route('/login', methods=['POST'])
def login_user():
    try:
        # Get the username and password from the request JSON
        data = request.get_json()
        print(f"Received data: {data}")  # Debug: Check what data was received

        username = data.get('username')
        password = data.get('password')

        # Validate if both username and password are provided
        if not username or not password:
            print(f"Missing username or password")  # Debug
            return jsonify({"error": "Nom d'utilisateur ou mot de passe manquant."}), 400

        # Fetch user from the database by username
        user = User.query.filter_by(username=username).first()

        # Check if user exists and if password matches
        if not user or not user.check_password(password):
            print(f"Invalid username or password")  # Debug
            return jsonify({"error": "Nom d'utilisateur ou mot de passe invalide."}), 401

        # Store user information in the session
        session['user'] = {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
        print(f"User logged in: {user.username}")  # Debug: Log the username

        # Send response with success message and dashboard redirect URL
        return jsonify({
            "message": "Connexion réussie.",
            "redirect_url": "/dashboard",  # Add redirect URL for the dashboard
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug: Log any exception
        return jsonify({"error": f"Erreur serveur: {str(e)}"}), 500

