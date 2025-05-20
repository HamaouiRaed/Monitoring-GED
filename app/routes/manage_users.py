from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.user import User
from flask_login import login_required

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    users_db = User.query.all()
    users = {
        u.username: {
            'name': u.name,
            'email': u.email,
            'role': u.role
        } for u in users_db
    }

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')

        if action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')

            email_exists = User.query.filter_by(email=email).first()
            username_exists = User.query.filter_by(username=username).first()

            if email_exists or username_exists:
                if email_exists:
                    flash("❌ Cet email est déjà utilisé.", "error")
                if username_exists:
                    flash("❌ Ce nom d'utilisateur existe déjà.", "error")
                return redirect(url_for('admin_bp.manage_users'))

            new_user = User(
                name=name,
                username=username,
                email=email,
                role=role
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("✅ Utilisateur ajouté avec succès.", "success")

        elif action == 'delete':
            user = User.query.filter_by(username=username).first()
            if user and user.username != 'admin':
                db.session.delete(user)
                db.session.commit()
                flash("✅ Utilisateur supprimé avec succès.", "success")

        elif action == 'update':
            new_name = request.form.get("name")
            new_email = request.form.get("email")
            new_role = request.form.get("role")
            new_password = request.form.get("password")

            user = User.query.filter_by(username=username).first()

            if user:
                # vérifier que l'email ne soit pas utilisé par un autre
                existing_email_user = User.query.filter(User.email == new_email, User.username != username).first()
                if existing_email_user:
                    flash("❌ Cet email est déjà utilisé par un autre utilisateur.", "error")
                    return redirect(url_for('admin_bp.manage_users'))

                user.name = new_name
                user.email = new_email
                user.role = new_role
                if new_password:
                    user.set_password(new_password)

                db.session.commit()
                flash("✅ Utilisateur mis à jour avec succès.", "success")
            else:
                flash("❌ Utilisateur introuvable.", "error")

        return redirect(url_for('admin_bp.manage_users'))

    return render_template('manage_users.html', users=users, username='admin', role='admin')
