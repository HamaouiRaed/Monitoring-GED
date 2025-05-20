from flask import Blueprint, request, jsonify
from datetime import datetime
from app.data.bases import BASES_LIST

update_pie_bp = Blueprint("update_pie", __name__)

@update_pie_bp.route('/update_pie', methods=['POST'])
def update_pie():
    data = request.get_json()
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except Exception:
        return jsonify({"labels": [], "values": []})

    # Utiliser les vraies valeurs depuis BASES_LIST
    results = [
        (base["name"], base["count"])
        for base in BASES_LIST
        if base["status"] == 1 and base["count"] > 0
    ]

    labels = [r[0] for r in results]
    values = [r[1] for r in results]

    return jsonify({"labels": labels, "values": values})
