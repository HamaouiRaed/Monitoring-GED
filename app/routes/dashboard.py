from flask import Blueprint, app, render_template, session, redirect, url_for, jsonify

dashboard = Blueprint("dashboard", __name__)

# Dashboard route to display user information and role-based links
@dashboard.route('/dashboard', methods=['GET'])
def dashboard_user():
    user = session.get('user')  # Fetch user data from the session

    if not user:
        return redirect(url_for('login_user'))  # Redirect to login if user is not authenticated

    # Render the dashboard template with the user data
    return render_template('dashboard.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)