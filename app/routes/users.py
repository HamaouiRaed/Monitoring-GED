from flask import Blueprint, render_template, jsonify
from app.models.user import User

user_bp = Blueprint("users", __name__)

# Route to return the HTML page with the JS table
@user_bp.route('/users', methods=['GET'])
def users_page():
    return render_template('usersTable.html')  # Static page that fetches data via JS

# API route that returns JSON data for the table
@user_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
