import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.models.user import User
from flask_login import login_required, current_user

files_bp = Blueprint('files', __name__, url_prefix='/files')

@files_bp.route('/manage_files', methods=['GET', 'POST'])
@login_required
def manage_files():
    current_username = current_user.username
    user = User.query.filter_by(username=current_username).first()

    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    files_dir = os.path.join(os.getcwd(), "logs")
    files_list = os.listdir(files_dir)

    allowed_extensions = {'.log', '.txt'}

    if request.method == 'POST':
        if 'file_upload' in request.files:
            file = request.files['file_upload']
            if file.filename:
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in allowed_extensions:
                    file.save(os.path.join(files_dir, file.filename))
                    flash(f"✅ Fichier {file.filename} uploadé avec succès.", "success")
                else:
                    flash("❌ Seuls les fichiers .log ou .txt sont autorisés.", "error")

        elif 'delete_file' in request.form:
            file_to_delete = request.form['delete_file']
            path = os.path.join(files_dir, file_to_delete)
            if os.path.exists(path):
                os.remove(path)
                flash(f"✅ Fichier {file_to_delete} supprimé avec succès.", "success")

        return redirect(url_for('files.manage_files'))

    return render_template('manage_files.html', page_title="Gérer les fichiers Logs", files=files_list, user=user)
