from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import current_user

from app.data import domaines as domaine_ctrl

domaine = Blueprint("domaines", __name__)

@domaine.route('/domaines', methods=['GET'])
def domaines_data():
    return render_template('domainesTable.html', user=current_user)

@domaine.route('/api/domaines', methods=['GET'])
def get_domaines():
    status = request.args.get('status', type=str)
    domaine_list = domaine_ctrl.get_all_domaines(status)  # This must return a list of dicts
    return jsonify(domaine_list)
