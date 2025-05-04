from flask import Blueprint, session, jsonify

logout = Blueprint("logout", __name__)

@logout.route('/logout', methods=['GET'])
def logout_user():
    session.pop('user', None)
    return jsonify({"message": "Déconnexion réussie."}), 200
