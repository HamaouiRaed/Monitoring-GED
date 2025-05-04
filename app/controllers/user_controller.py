from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import User

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

@user_bp.route('/admin/users', methods=['GET'])
@login_required
def view_users():
    users = User.query.all()
    return render_template('admin/view_users.html', users=users)


# ------------------------ Count Users ------------------------

@user_bp.route('/admin/users/count', methods=['GET'])
@login_required
def count_users():
    count = User.query.count()
    return jsonify({'user_count': count})


# ------------------------ View Single User ------------------------

@user_bp.route('/user/<int:id>', methods=['GET'])
@login_required
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('admin/view_user.html', user=user)


# ------------------------ Edit User ------------------------

@user_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
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
def delete_user(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash("You cannot delete your own account!", 'danger')
        return redirect(url_for('users.view_user', id=user.id))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", 'success')
    return redirect(url_for('users.view_users'))
