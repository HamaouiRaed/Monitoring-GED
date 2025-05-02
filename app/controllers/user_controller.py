from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import db
from app.models import User

user_bp = Blueprint('user', __name__)

# ------------------------ Registration Route ------------------------

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", 'danger')
            return redirect(url_for('user.register'))

        # Create new user and hash the password
        new_user = User(username=username, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("User successfully created!", 'success')
        return redirect(url_for('user.view_users'))

    return render_template('register.html')


# ------------------------ View All Users ------------------------

@user_bp.route('/admin/users', methods=['GET'])
def view_users():
    users = User.query.all()
    return render_template('admin/view_users.html', users=users)


# ------------------------ Count Users ------------------------

@user_bp.route('/admin/users/count', methods=['GET'])
def count_users():
    count = User.query.count()
    return jsonify({'user_count': count})


# ------------------------ View Single User ------------------------

@user_bp.route('/user/<int:id>', methods=['GET'])
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template('user/view_user.html', user=user)


# ------------------------ Edit User ------------------------

@user_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        password = request.form.get('password')
        
        # If a new password is provided, hash and update it
        if password:
            user.set_password(password)

        db.session.commit()
        flash("User details successfully updated!", 'success')
        return redirect(url_for('user.view_user', id=user.id))

    return render_template('user/edit_user.html', user=user)


# ------------------------ Delete User ------------------------

@user_bp.route('/user/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)

    # Make sure the user is not trying to delete themselves
    if user.id == current_user.id:
        flash("You cannot delete your own account!", 'danger')
        return redirect(url_for('user.view_user', id=user.id))

    db.session.delete(user)
    db.session.commit()
    flash("User successfully deleted!", 'success')
    return redirect(url_for('user.view_users'))
