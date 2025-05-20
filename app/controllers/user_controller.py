from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from app import db
from app.models.user import User
import os
from .decorators import admin_required


user_bp = Blueprint('users', __name__)

# ------------------------ Register ------------------------

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'user').strip()

        if not name or not username or not email or not password:
            flash("All fields are required.", 'danger')
            return redirect(url_for('users.register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or Email already exists!", 'danger')
            return redirect(url_for('users.register'))

        new_user = User(name=name, username=username, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("User created successfully!", 'success')
        return redirect(url_for('users.view_users'))

    return render_template('auth/register.html')

# ------------------------ View All Users ------------------------

@user_bp.route('/admin/users', methods=['GET'], endpoint='view_users')
@login_required
def view_users():
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))
    users = User.query.all()
    return render_template('admin/view_users.html', users=users)

# ------------------------ Count Users ------------------------

@user_bp.route('/admin/users/count', methods=['GET'])
@login_required
def count_users():
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))
    count = User.query.count()
    return jsonify({'user_count': count})

# ------------------------ View Single User ------------------------

@user_bp.route('/admin/users', methods=['GET'], endpoint='view_users')
@login_required
@admin_required
def view_user(id):
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))
    user = User.query.get_or_404(id)
    return render_template('admin/view_user.html', user=user)

# ------------------------ Edit User ------------------------

@user_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form.get('username').strip()
        user.role = request.form.get('role').strip()
        password = request.form.get('password')

        if password:
            user.set_password(password)

        db.session.commit()
        flash("User updated successfully!", 'success')
        return redirect(url_for('users.view_user', id=user.id))

    return render_template('admin/edit_user.html', user=user)

# ------------------------ Delete User ------------------------

@user_bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash("You cannot delete your own account!", 'danger')
        return redirect(url_for('users.view_user', id=user.id))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", 'success')
    return redirect(url_for('users.view_users'))

# ------------------------ Manage Users ------------------------

@user_bp.route("/admin/manage_users", methods=["GET", "POST"])
@login_required
@admin_required
def manage_users():
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))

    message = ""
    if request.method == "POST":
        action = request.form["action"]
        username = request.form["username"].strip()

        if action == "add":
            password = request.form["password"].strip()
            role = request.form["role"].strip()
            email = request.form.get("email", "").strip()
            name = request.form.get("name", "").strip()

            if User.query.filter_by(username=username).first():
                message = f"Le nom d'utilisateur {username} existe déjà."
            else:
                new_user = User(name=name, username=username, email=email, role=role)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                message = f"Utilisateur {username} ajouté."

        elif action == "delete":
            user = User.query.filter_by(username=username).first()
            if user:
                if user.username == "admin":
                    message = "Impossible de supprimer l'utilisateur admin."
                else:
                    db.session.delete(user)
                    db.session.commit()
                    message = f"Utilisateur {username} supprimé."

    users = User.query.all()
    return render_template("manage_users.html", users=users, message=message)

# ------------------------ Manage Files ------------------------

@user_bp.route("/admin/manage_files", methods=["GET", "POST"])
@login_required
@admin_required
def manage_files():
    if session.get("role") != "admin":
        flash("Accès refusé.", "danger")
        return redirect(url_for("main.unauthorized"))

    message = ""
    files_dir = os.getcwd()
    files = os.listdir(files_dir)

    if request.method == "POST":
        if "file_upload" in request.files:
            file = request.files["file_upload"]
            file.save(os.path.join(files_dir, file.filename))
            message = f"Fichier {file.filename} uploadé avec succès."
        elif "delete_file" in request.form:
            file_to_delete = request.form["delete_file"]
            file_path = os.path.join(files_dir, file_to_delete)
            if os.path.exists(file_path):
                os.remove(file_path)
                message = f"Fichier {file_to_delete} supprimé avec succès."

    return render_template("manage_files.html", files=files, message=message)
