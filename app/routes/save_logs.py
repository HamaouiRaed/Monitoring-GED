from flask import Flask, Blueprint, render_template, request
from flask_login import login_required, current_user
import os
import re
import pandas as pd

logs_bp = Blueprint("logs", __name__)
# ------------------------------ Utilitaires de parsing
def parse_log_file(file_path):
    data = []
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["DateDebat", "FileName", "Application", "ErrorCode", "ErrorDescription"])

    with open(file_path, 'r', encoding='ISO-8859-1', errors='ignore') as file:
        date_pattern = re.compile(r'----- DBAET Début - (\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}) -----')
        file_name_pattern = re.compile(r"Fichier:\s+.+?DBBATCHWORK\\\\(.+)")
        base_pattern = re.compile(r'\s*Base:\s*(\S+)')
        error_code_pattern = re.compile(r'\[([A-Fa-f0-9]{4},\d{2})\]')
        error_description_pattern = re.compile(r'\[.*?\](.*)')

        current_date, current_file, current_base = None, None, "Non spécifiée"

        for line in file:
            if match := date_pattern.search(line):
                current_date = match.group(1)
            if match := file_name_pattern.search(line):
                current_file = match.group(1)
            if match := base_pattern.search(line):
                current_base = match.group(1)
            if (code := error_code_pattern.search(line)) and (desc := error_description_pattern.search(line)):
                data.append({
                    "DateDebat": current_date or "Date non trouvée",
                    "FileName": current_file or "Fichier non trouvé",
                    "Application": current_base,
                    "ErrorCode": code.group(1),
                    "ErrorDescription": desc.group(1).strip()
                })
    return pd.DataFrame(data)

def parse_journal_fusion(file_path):
    data = []
    date_str = ""
    base_name = ""
    lot_size = 500
    total_files = 0

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["Date", "Base", "NomBase", "Lot", "Statut", "FichiersReçus"])

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    # Lire toutes les lignes pour extraire le total et traiter ensuite
    for line in lines:
        if m := re.search(r'Date actuelle\s*:\s*(\d{8}|\d{4}/\d{2}/\d{2})', line):
            raw_date = m.group(1)
            date_str = f"{raw_date[:4]}/{raw_date[4:6]}/{raw_date[6:]}" if "/" not in raw_date else raw_date
        elif m := re.search(r'Nom de base des lots\s*:\s*(\S+)', line):
            base_name = m.group(1)
        elif m := re.search(r'Nombre total de fichiers traités\s*:\s*(\d+)', line):
            total_files = int(m.group(1))

    # Compter les succès et échecs par lot
    for line in lines:
        if m := re.search(r'Lot (\d+) fusionné avec succès\s*:\s*(.*\.pdf)', line):
            lot_num = int(m.group(1))
            files_count = min(lot_size, total_files - lot_size * (lot_num - 1))
            data.append({
                "Date": date_str,
                "Base": base_name,
                "Référence document": base_name,
                "Lot": f"Lot {lot_num}",
                "Statut": "Succès",
                "FichiersReçus": files_count
            })
        elif m := re.search(r'Échec de la fusion du lot (\d+)', line):
            lot_num = int(m.group(1))
            files_count = min(lot_size, total_files - lot_size * (lot_num - 1))
            data.append({
                "Date": date_str,
                "Base": base_name,
                "Référence document": base_name,
                "Lot": f"Lot {lot_num}",
                "Statut": "Échec",
                "FichiersReçus": files_count
            })

    if not data:
        data.append({
            "Date": date_str or "-",
            "Base": base_name or "-",
            "Référence document": base_name or "-",
            "Lot": "-",
            "Statut": "Aucun lot détecté",
            "FichiersReçus": "-"
        })
    return pd.DataFrame(data)



# ------------------------------ Page principale de logs
@logs_bp.route('/logs-archivage', methods=["GET", "POST"])
@login_required
def logs_archivage():
    logs = []
    fusion_data = None
    error_message = None

    # Reçu du formulaire
    date_filter = request.form.get("date", "").strip()
    selected_type = request.form.get("log_type", "")
    error_code_filter = request.form.get("error_code", "").strip()

    # Dossier contenant les fichiers logs
    logs_dir = os.path.join(os.getcwd(), "logs")
    available_logs = [f for f in os.listdir(logs_dir)
                      if (f.endswith(".log") or f.endswith(".txt")) and not f.startswith(".")]
    matching_files = []

    for file in available_logs:
        file_path = os.path.join(logs_dir, file)

        if file.lower().startswith("journal"):
            df_fusion = parse_journal_fusion(file_path)

            if not date_filter or (date_filter and any(date_filter in str(val) for val in df_fusion["Date"].unique())):
                matching_files.append(file)

                if selected_type.strip() == file.strip():
                    fusion_data = df_fusion.to_dict(orient="records")  # ✅ transforme en liste de dicts

        else:
            df = parse_log_file(file_path)
            if not df.empty:
                filtered_df = df
                if date_filter:
                    filtered_df = filtered_df[
                        filtered_df["DateDebat"].astype(str).str.contains(date_filter, na=False)
                    ]
                if not filtered_df.empty:
                    matching_files.append(file)

                    if selected_type == file:
                        if error_code_filter:
                            filtered_df = filtered_df[
                                filtered_df["ErrorCode"].str.contains(error_code_filter, na=False)
                            ]
                        logs = filtered_df.to_dict(orient="records")

    # Gestion des messages d'erreur
    if request.method == "POST":
        if not matching_files:
            error_message = f"Aucun résultat trouvé pour la date {date_filter}."
        elif selected_type and selected_type not in matching_files:
            error_message = f"Aucun résultat trouvé pour le fichier {selected_type} à la date {date_filter}."
        elif not selected_type.lower().startswith("journal") and error_code_filter and not logs:
            error_message = f"Aucun résultat trouvé pour le fichier {selected_type} à la date {date_filter} avec le code erreur '{error_code_filter}'."

    return render_template(
        "logs_automate.html",
        user=current_user,
        logs=logs,
        fusion_data=fusion_data,
        selected_type=selected_type,
        document_filter=date_filter,
        error_code_filter=error_code_filter,
        available_logs=matching_files,
        error_message=error_message
    )


@logs_bp.route('/download-csv/<log_type>', methods=['GET'])
@login_required
def download_csv(log_type):
    from flask import send_file

    logs_dir = os.path.join(os.getcwd(), "logs")
    file_path = os.path.join(logs_dir, log_type)

    # 📌 Vérifie si c'est un journal fusion
    if log_type.lower().startswith("journal"):
        df = parse_journal_fusion(file_path)  # ⬅️ retourne un DataFrame directement
    else:
        df = parse_log_file(file_path)

    # 📥 Création du fichier CSV
    csv_path = os.path.join(logs_dir, f"{log_type}_export.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    return send_file(csv_path, as_attachment=True)





