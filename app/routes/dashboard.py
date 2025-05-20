
from flask import Blueprint, render_template, session, redirect, url_for, make_response
from flask_login import login_required

dashboard = Blueprint("dashboard", __name__)

@dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_user():
    username = session.get('username')
    role = session.get('role')

    if not username or not role:
        return redirect(url_for('login.login_page'))



    # ✅ Empêche le cache navigateur
    response = make_response(render_template(
        'dashboard.html',
        username=username,
        role=role,  # 👈 transmis au template
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
@dashboard.route('/fusion-table')
@login_required
def fusion_table():
    return render_template("fusion_table.html")