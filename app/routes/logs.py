from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import os
import re
import pandas as pd
from datetime import datetime




def normalize_date(date_str):
    if not date_str:
        return ""

    # Liste des formats possibles acceptés (inclus le HTML et texte manuel)
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y%m%d"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    return ""  # Si aucun format ne matche


logs_bp = Blueprint("logs", __name__)
# ------------------------------ Utilitaires de parsing
def parse_log_file(file_path):
    data = []
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=[
            "DateDebat", "NomDeDocument", "Application", "ErrorCode", "ErrorDescription"
        ])

    with open(file_path, 'r', encoding='ISO-8859-1', errors='ignore') as file:
        # Regex patterns
        pdf_line_pattern = re.compile(
            r'(\d{2}/\d{2}/\d{4})\s*[:\-]\s*(\d{2}:\d{2}:\d{2}).*?([A-Za-z0-9_-]+\.PDF)', re.IGNORECASE
        )
        base_pattern = re.compile(r'\s*Base:\s*(\S+)')
        error_code_pattern = re.compile(r'\[([A-Fa-f0-9]{4},\d{2})\]')
        error_description_pattern = re.compile(r'\[.*?\](.*)')

        current_base = "Non spécifiée"
        current_date = None
        current_pdf = None

        buffer = []  # contient temporairement les erreurs liées à un bloc

        for line in file:
            # Mise à jour base si présente
            if match := base_pattern.search(line):
                current_base = match.group(1)

            # Si une ligne contient date + nom du document PDF → nouveau bloc
            if match := pdf_line_pattern.search(line):
                # Sauvegarder les erreurs précédentes avant de commencer un nouveau bloc
                for err in buffer:
                    data.append({
                        "DateDebat": current_date,
                        "NomDeDocument": current_pdf,
                        "Application": current_base,
                        "ErrorCode": err["ErrorCode"],
                        "ErrorDescription": err["ErrorDescription"]
                    })
                buffer.clear()

                date_str, heure_str, doc_name = match.groups()
                current_date = f"{date_str} - {heure_str}"
                current_pdf = doc_name

            # Récupération code erreur + message
            code = error_code_pattern.search(line)
            desc = error_description_pattern.search(line)

            if code and desc and current_date and current_pdf:
                buffer.append({
                    "ErrorCode": code.group(1),
                    "ErrorDescription": desc.group(1).strip()
                })

        # Fin de fichier : ajouter les erreurs restantes
        for err in buffer:
            data.append({
                "DateDebat": current_date,
                "NomDeDocument": current_pdf,
                "Application": current_base,
                "ErrorCode": err["ErrorCode"],
                "ErrorDescription": err["ErrorDescription"]
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
            date_str = raw_date.replace("/", "")  # ✅ Corrigé ici pour toujours avoir YYYYMMDD
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



# ------------------------------ route de logs automate
@logs_bp.route('/logs-archivage/automate', methods=["GET", "POST"])
@login_required
def logs_automate():
    logs = []
    error_message = None
    show_results = False

    date_filter = ""
    selected_type = ""
    error_code_filter = ""
    matching_files = []
    available_logs = []

    logs_dir = os.path.join(os.getcwd(), "logs")

    # 📁 Récupérer les fichiers disponibles à tout moment (affichés dans le select)
    for f in os.listdir(logs_dir):
        if f.endswith((".log", ".txt")) and not f.startswith("journal"):
            available_logs.append(f)

    # ✅ Ne traiter les données que si la requête est POST (formulaire soumis)
    if request.method == "POST":
        date_filter = request.form.get("date", "").strip()
        selected_type = request.form.get("log_type", "")
        error_code_filter = request.form.get("error_code", "").strip()

        # 🗓️ Convertir au format lisible
        date_filter_formatted = ""
        if date_filter:
            try:
                date_filter_formatted = datetime.strptime(date_filter, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                date_filter_formatted = date_filter

        if selected_type:
            selected_path = os.path.join(logs_dir, selected_type)

            if os.path.exists(selected_path):
                df = parse_log_file(selected_path)

                if not df.empty:
                    if date_filter_formatted:
                        df["DateDebat"] = pd.to_datetime(df["DateDebat"], dayfirst=True, errors="coerce").dt.strftime("%d/%m/%Y")
                        df = df[df["DateDebat"] == date_filter_formatted]

                    if not df.empty:
                        matching_files.append(selected_type)

                        if error_code_filter:
                            df = df[df["ErrorCode"].str.contains(error_code_filter, na=False)]

                        logs = df.to_dict(orient="records")
                        if logs:
                            show_results = True

        # 🔔 Gestion des messages utilisateur
        if not matching_files:
            error_message = f"Aucun résultat trouvé pour la date {date_filter}."
        elif selected_type and selected_type not in matching_files:
            error_message = f"Aucun résultat trouvé pour le fichier {selected_type}."
        elif error_code_filter and not logs:
            error_message = f"Aucun log contenant le code erreur '{error_code_filter}' trouvé dans {selected_type}."

    return render_template(
        "logs_automate.html",
        active_page="automate",
        user=current_user,
        logs=logs,
        selected_type=selected_type,
        document_filter=date_filter,
        error_code_filter=error_code_filter,
        available_logs=available_logs,
        error_message=error_message,
        matching_files=matching_files,
        show_results=show_results
    )

#____________journal_fusion___________

@logs_bp.route('/logs-archivage/fusion', methods=['GET', 'POST'])
@login_required
def logs_journal_fusion():


    fusion_data = None
    error_message = None
    success_total = 0
    failure_total = 0
    show_results = False

    # 🔁 Récupération des filtres
    base_filter = request.form.get("base_filter", "").strip()
    date_filter_raw = request.form.get("date", "").strip()
    selected_type = request.form.get("log_type", "").strip()

    date_filter_raw = request.form.get("date", "").strip()
    date_filter = normalize_date(date_filter_raw)

    logs_dir = os.path.join(os.getcwd(), "logs")
    available_logs = []
    matching_files = []
    unique_bases = []

    # 📂 Lister les fichiers valides
    for f in os.listdir(logs_dir):
        if f.startswith("journal") and f.endswith((".log", ".txt")):
            file_path = os.path.join(logs_dir, f)
            df = parse_journal_fusion(file_path)

            # ✅ Convertir les dates après chargement du fichier
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y%m%d")

            # ✅ Condition corrigée
            if not df.empty and (
                    not date_filter or date_filter in df["Date"].astype(str).values
            ):
                available_logs.append(f)

    # ✅ Traitement uniquement en POST
    if request.method == "POST" and selected_type:
        file_path = os.path.join(logs_dir, selected_type)

        if os.path.exists(file_path):
            df = parse_journal_fusion(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y%m%d")

            if not df.empty:
                # 🎯 Filtrage par date exacte
                if date_filter:
                    df = df[df['Date'].astype(str) == date_filter]
                # 🎯 Filtrage par base
                if base_filter:
                    df = df[df['Base'].astype(str).str.contains(base_filter, na=False)]

                if not df.empty:
                    fusion_data = df.to_dict(orient='records')
                    unique_bases = sorted(df['Base'].unique())
                    matching_files.append(selected_type)

                    success_total = sum(int(row['FichiersReçus']) for row in fusion_data if row['Statut'] == "Succès")
                    failure_total = sum(int(row['FichiersReçus']) for row in fusion_data if row['Statut'] == "Échec")

                    show_results = True
        else:
            error_message = f"Le fichier sélectionné n'existe pas : {selected_type}"

        if not available_logs:
            error_message = f"Aucun fichier disponible pour la date {date_filter_raw}."
        elif selected_type and selected_type not in matching_files:
            error_message = f"Aucune donnée disponible pour le fichier {selected_type}."

    return render_template(
        "journal_fusion.html",
        user=current_user,
        active_page="fusion",
        fusion_data=fusion_data,
        selected_type=selected_type,
        document_filter=date_filter_raw,
        base_filter=base_filter,
        available_logs=available_logs,
        unique_bases=unique_bases,
        error_message=error_message,
        success_total=success_total,
        failure_total=failure_total,
        show_results=show_results
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





