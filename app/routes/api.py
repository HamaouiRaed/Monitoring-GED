from flask import Blueprint, jsonify, request
from app.controllers import base_controller as base_ctrl
from app.controllers import domaine_controller as domaine_ctrl
from app.controllers.base_controller import count_active_bases, count_inactive_bases
from app.controllers.domaine_controller import count_active_domaines, count_inactive_domaines
from app.models.user import User
from app import db
import jwt
import datetime
import logging
from werkzeug.security import check_password_hash

api = Blueprint('api', __name__)

# ---------------------- User API ----------------------
@api.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not name or not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or Email already exists"}), 400

    user = User(name=name, username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

@api.route('/api/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logging.debug(f"Login attempt for user: {username}")

    # Check if username exists
    user = User.query.filter_by(username=username).first()
    if not user:
        logging.debug(f"User {username} not found.")
        return jsonify({"error": "Invalid username or password"}), 401

    # Check if password matches
    if user and user.check_password(password):
        logging.debug(f"User {username} logged in successfully.")
        return jsonify({"message": "Login successful!", "user": user.to_dict()}), 200
    else:
        logging.debug(f"Invalid password for user: {username}")
        return jsonify({"error": "Invalid username or password"}), 401


@api.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@api.route('/api/user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.name = data.get('name', user.name)
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    password = data.get('password')

    if password:
        user.set_password(password)

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@api.route('/api/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@api.route('/api/users/count', methods=['GET'])
def get_users_count():
    count = User.query.count()
    return jsonify({"user_count": count})

# ---------------------- Bases API ----------------------
@api.route('/api/bases', methods=['GET'])
def get_bases():
    status = request.args.get('status', type=str)
    bases = base_ctrl.get_all_bases(status)
    return jsonify(bases)

@api.route('/api/bases/<int:id>', methods=['GET'])
def get_base(id):
    base = base_ctrl.get_base_by_id(id)
    if base:
        return jsonify(base)
    return jsonify({'error': 'Base not found'}), 404

@api.route('/api/bases/count', methods=['GET'])
def get_bases_count():
    status = request.args.get('status', type=int)
    base_count = base_ctrl.count_bases(status)
    return jsonify({"count": base_count})

@api.route("/api/bases/active", methods=["GET"])
def get_active_bases():
    return jsonify(base_ctrl.get_active_bases())

@api.route("/api/bases/inactive", methods=["GET"])
def get_inactive_bases():
    return jsonify(base_ctrl.get_inactive_bases())

@api.route("/api/bases/active/count", methods=["GET"])
def count_active_bases_route():
    return jsonify({"active_count": count_active_bases()})

@api.route("/api/bases/inactive/count", methods=["GET"])
def count_inactive_bases_route():
    return jsonify({"inactive_count": count_inactive_bases()})

# ---------------------- Domaines API ----------------------
@api.route('/api/domaines', methods=['GET'])
def get_domaines():
    status = request.args.get('status', type=str)
    return jsonify(domaine_ctrl.get_all_domaines(status))

@api.route('/api/domaines/<int:id>', methods=['GET'])
def get_domaine(id):
    domaine = domaine_ctrl.get_domaine_by_id(id)
    if domaine:
        return jsonify(domaine)
    return jsonify({'error': 'Domaine not found'}), 404

@api.route('/api/domaines/count', methods=['GET'])
def get_domaines_count():
    status = request.args.get('status', type=int)
    return jsonify({"count": domaine_ctrl.count_domaines(status)})

@api.route("/api/domaines/active", methods=["GET"])
def get_active_domaines():
    return jsonify(domaine_ctrl.get_active_domaines())

@api.route("/api/domaines/inactive", methods=["GET"])
def get_inactive_domaines():
    return jsonify(domaine_ctrl.get_inactive_domaines())

@api.route("/api/domaines/active/count", methods=["GET"])
def count_active_domaines_route():
    return jsonify({"active_count": count_active_domaines()})

@api.route("/api/domaines/inactive/count", methods=["GET"])
def count_inactive_domaines_route():
    return jsonify({"inactive_count": count_inactive_domaines()})
