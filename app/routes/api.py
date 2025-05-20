from flask import Blueprint, jsonify, request
from app.models.user import User
from app import db
import jwt
from config import Config
from functools import wraps
from app.controllers import base_controller as base_ctrl
from app.controllers import domaine_controller as domaine_ctrl
import os
import re



api = Blueprint('api', __name__)

# Secret key for JWT encoding
SECRET_KEY = Config.SECRET_KEY


# ---------------------- User API ----------------------

@api.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json()

    name = data.get('name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')


    # Validate all required fields
    if not all([name, username, email, password]):
        return jsonify({"error": "All fields (name, username, email, password) are required."}), 400

    # Check for existing user by username or email
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({"error": "Username or email already exists."}), 400

    # Create and save user
    new_user = User(name=name, username=username, email=email, role=role)
    new_user.set_password(password)  # Ensure this hashes the password

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

 

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


# ---------------------- Token Authorization Helper ----------------------

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # "Bearer <token>"

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])  # Fetch user using ID from token
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)
    
    return decorated_function


# ---------------------- Bases and Domaines API ----------------------

# Your bases and domaines API code remains unchanged as they are correct.


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


@api.route('/api/bases/active', methods=['GET'])
def get_active_bases():
    return jsonify(base_ctrl.get_active_bases())


@api.route('/api/bases/inactive', methods=['GET'])
def get_inactive_bases():
    return jsonify(base_ctrl.get_inactive_bases())


@api.route('/api/bases/active/count', methods=['GET'])
def count_active_bases_route():
    return jsonify({"active_count": base_ctrl.count_active_bases()})


@api.route('/api/bases/inactive/count', methods=['GET'])
def count_inactive_bases_route():
    return jsonify({"inactive_count": base_ctrl.count_inactive_bases()})


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


@api.route('/api/domaines/active', methods=['GET'])
def get_active_domaines():
    return jsonify(domaine_ctrl.get_active_domaines())


@api.route('/api/domaines/inactive', methods=['GET'])
def get_inactive_domaines():
    return jsonify(domaine_ctrl.get_inactive_domaines())


@api.route('/api/domaines/active/count', methods=['GET'])
def count_active_domaines_route():
    return jsonify({"active_count": domaine_ctrl.count_active_domaines()})


@api.route('/api/domaines/inactive/count', methods=['GET'])
def count_inactive_domaines_route():
    return jsonify({"inactive_count": domaine_ctrl.count_inactive_domaines()})

from app.routes.documents_archives import get_total_documents_from_journal_dir  # ✅ Correct
@api.route('/api/documents/count', methods=['GET'])
def get_documents_count():
    logs_dir = os.path.join(os.getcwd(), 'logs')
    total = get_total_documents_from_journal_dir(logs_dir)
    return jsonify({'documentsCount': total})
@api.route('/api/fusion-table', methods=['GET'])
def get_fusion_summary():
    logs_dir = os.path.join(os.getcwd(), "logs")
    result = []

    for file in os.listdir(logs_dir):
        if file.lower().startswith("journal") and file.endswith((".log", ".txt")):
            path = os.path.join(logs_dir, file)
            date, base = "", ""
            total_files = 0
            error_message = "Pas d'erreur"

            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                for line in lines:
                    if m := re.search(r'Date actuelle\s*:\s*(\d{8})', line):
                        date = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"
                    elif m := re.search(r'Nom de base des lots\s*:\s*(\S+)', line):
                        base = m.group(1)
                    elif m := re.search(r'Nombre total de fichiers traités\s*:\s*(\d+)', line):
                        total_files = int(m.group(1))
                    elif "[ERREUR]" in line:
                        status = "Échec"
                        error_message = line.strip()

                result.append({
                    "date": date or "-",
                    "base": base or "-",
                    "fichiers": total_files,
                    "erreur": error_message
                })

            except Exception as e:
                result.append({
                    "date": "-",
                    "base": file,
                    "fichiers": 0,
                    "erreur": str(e)
                })

    return jsonify(result)



