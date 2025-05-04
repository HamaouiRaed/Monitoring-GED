from flask import Blueprint, render_template, redirect, url_for

main = Blueprint("main", __name__)

@main.route("/")
def index():
    # Redirect to the login page
    return redirect(url_for('main.login'))

@main.route("/login")
def login():
    # Render the login page template
    return render_template("login.html")
