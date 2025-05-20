
from flask import Blueprint, render_template
from flask_jwt_extended import current_user

card = Blueprint("cards", __name__)
@card.route('/cards')
def cards_data():
    return render_template('cards.html', user=current_user)  # if using login

