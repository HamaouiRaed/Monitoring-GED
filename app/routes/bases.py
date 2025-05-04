from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import current_user

from app.data import bases as base_ctrl

base = Blueprint("bases", __name__)

@base.route('/bases', methods=['GET'])
def bases_data():
    return render_template('basesTable.html', user=current_user)

@base.route('/api/bases', methods=['GET'])
def get_bases():
    status = request.args.get('status', type=str)
    base_list = base_ctrl.get_all_bases(status)  # This must return a list of dicts
    return jsonify(base_list)
