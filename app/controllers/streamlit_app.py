import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import chardet

# -------------------- CSS --------------------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #F4F6F5;
        color: #1E2D2F;
    }

    .stTitle h1 {
        font-weight: 800;
        font-size: 2.2em;
        color: #004D43;
        margin-bottom: 0.2em;
    }

    .stFileUploader {
        border: 2px dashed #007F73 !important;
        background-color: #ffffff !important;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 3px 8px rgba(0, 127, 115, 0.1);
    }

    .custom-button {
        background-color: #00B8A9;
        color: white !important;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        display: inline-block;
        transition: background-color 0.3s ease;
    }

    .custom-button:hover {
        background-color: #007F73;
        color: white !important;
    }

    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.title("📁 Menu")
    st.markdown("""
        <a href="http://localhost:5000/dashboard" target="_self">
            <button style='background-color:#00B8A9;color:white;padding:10px 20px;border:none;border-radius:8px;font-weight:bold;font-size:16px;width:100%;cursor:pointer;'>
                🏠 Retour au Dashboard
            </button>
        </a>
    """, unsafe_allow_html=True)

# -------------------- Titre --------------------
st.title("📊 Analyse et Visualisation des Logs d'Erreur")

# -------------------- Encodage --------------------
def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

# -------------------- Parser classique --------------------
def parse_log_file(file):
    date_pattern = re.compile(r'----- DBAET Début - (\d{2}/\d{2}/\d{4} - \d{2}:\d{2}:\d{2}) -----')
    file_name_pattern = re.compile(r"Fichier:\s+.+?DBBATCHWORK\\\\(.+)")
    error_code_pattern = re.compile(r'\[([A-Fa-f0-9]{4},\d{2})\]')
    error_description_pattern = re.compile(r'\[.*?\](.*)')

    data = []
    current_date = None
    current_file_name = None

    for line in file:
        if (m := date_pattern.search(line)):
            current_date = m.group(1)
        if (m := file_name_pattern.search(line)):
            current_file_name = m.group(1)
        if (code := error_code_pattern.search(line)) and (desc := error_description_pattern.search(line)):
            data.append({
                'DateDebat': current_date,
                'FileName': current_file_name,
                'ErrorCode': code.group(1),
                'ErrorDescription': desc.group(1).strip()
            })

    df = pd.DataFrame(data)
    df['DateDebat'] = pd.to_datetime(df['DateDebat'], errors='coerce').dt.date
    return df

# -------------------- Parser Journal Fusion --------------------
def parse_journal_fusion_df(file_lines):
    date, base_name, nb_fichiers_total = "", "", 0
    lots_data = []

    for line in file_lines:
        if m := re.search(r'Date actuelle\s*:\s*(\d{8})', line):
            raw_date = m.group(1)
            date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        elif m := re.search(r'Nom de base des lots\s*:\s*(\S+)', line):
            base_name = m.group(1)
        elif "fusionné avec succès" in line:
            lot_num = re.search(r'Lot\s*(\d+)', line)
            lots_data.append({
                "Date": date,
                "BaseName": base_name,
                "Lot": int(lot_num.group(1)) if lot_num else None,
                "Statut": "Succès",
                "Message": line.strip()
            })
        elif re.search(r'Échec de la fusion', line, re.IGNORECASE):
            lot_num = re.search(r'Lot\s*(\d+)', line)
            lots_data.append({
                "Date": date,
                "BaseName": base_name,
                "Lot": int(lot_num.group(1)) if lot_num else None,
                "Statut": "Échec",
                "Message": line.strip()
            })
        elif m := re.search(r'Nombre total de fichiers traités\s*:\s*(\d+)', line):
            nb_fichiers_total = int(m.group(1))

    # Répartition des fichiers par lot
    total_lots = len(lots_data)
    fichiers_restants = nb_fichiers_total
    for i, row in enumerate(lots_data):
        if fichiers_restants >= 500:
            lots_data[i]["FichiersTraites"] = 500
            fichiers_restants -= 500
        else:
            lots_data[i]["FichiersTraites"] = fichiers_restants
            fichiers_restants = 0

    return pd.DataFrame(lots_data)
# -------------------- Upload Fichier --------------------
uploaded_file = st.file_uploader("📂 Téléchargez un fichier .log ou .txt", type=["log", "txt"])

if uploaded_file:
    uploaded_file.seek(0)
    encoding = detect_encoding(uploaded_file)
    uploaded_file.seek(0)
    text = uploaded_file.read().decode(encoding, errors="replace")
    content = text.splitlines()

    if "Date actuelle" in text:
        fusion = parse_journal_fusion_df(content)

        # ✅ Calcul des indicateurs
        nb_succes = fusion[fusion["Statut"] == "Succès"].shape[0]
        nb_echecs = fusion[fusion["Statut"] == "Échec"].shape[0]
        total_fichiers = fusion["FichiersTraites"].sum()

        st.markdown("## 📂 Statistiques Journal Fusion")
        st.write(f"🗓️ Date : {fusion['Date'].iloc[0] if not fusion.empty else '-'}")
        st.write(f"📦 Base : {fusion['BaseName'].iloc[0] if not fusion.empty else '-'}")
        st.write(f"✅ Lots fusionnés avec succès : {nb_succes}")
        st.write(f"❌ Lots échoués : {nb_echecs}")
        st.write(f"📄 Total fichiers traités : {total_fichiers}")

        # ✅ Détail des lots
        st.markdown("### 📄 Détail des lots fusionnés avec succès")
        with st.expander("✅ Lots fusionnés"):
            for _, row in fusion[fusion["Statut"] == "Succès"].iterrows():
                st.code(row["Message"], language='')

        if nb_echecs > 0:
            with st.expander("⚠️ Détail des lots échoués"):
                for _, row in fusion[fusion["Statut"] == "Échec"].iterrows():
                    st.code(row["Message"], language='')

        # ✅ Visualisation
        st.markdown("### 📊 Visualisation des Résultats de Fusion")
        chart_type = st.selectbox("📈 Type de graphique :", ["Camembert", "Histogramme"], key="fusion_chart")
        labels = ["Succès", "Échec"]
        values = [nb_succes, nb_echecs]

        fig, ax = plt.subplots(figsize=(6, 4))
        if chart_type == "Camembert":
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=["#2ecc71", "#e74c3c"])
            ax.set_title("Répartition des lots fusionnés")
        else:
            ax.bar(labels, values, color=["#2ecc71", "#e74c3c"])
            ax.set_ylabel("Nombre de lots")
            ax.set_title("Fusion réussie vs échouée")
        st.pyplot(fig)

        # ✅ Fichiers reçus par lot
        if not fusion.empty and "FichiersTraites" in fusion.columns:
            st.markdown("### 📦 Répartition des Fichiers Reçus par Lot")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(fusion["Lot"], fusion["FichiersTraites"], color="#3498db")
            ax.set_xlabel("Lots")
            ax.set_ylabel("Fichiers Reçus")
            ax.set_title("Nombre de fichiers reçus par lot")
            st.pyplot(fig)

    else:
        df = parse_log_file(content)

        if not df.empty:
            st.subheader("🔍 Erreurs distinctes")
            st.dataframe(df.drop_duplicates(subset=['ErrorCode', 'ErrorDescription'])[['ErrorCode', 'ErrorDescription']], hide_index=True)

            st.success(f"✅ Nombre total d'erreurs : {len(df)}")

            if 'ErrorCode' in df.columns and 'DateDebat' in df.columns:
                error_counts = df.groupby(['DateDebat', 'ErrorCode']).size().unstack(fill_value=0)

                vis_type = st.selectbox("📈 Choisissez une visualisation :", ["Camembert", "Histogramme", "Courbe"])
                fig, ax = plt.subplots(figsize=(10, 5))

                if vis_type == "Camembert":
                    counts = df['ErrorCode'].value_counts()
                    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
                    ax.set_title("Répartition des Erreurs")
                elif vis_type == "Histogramme":
                    counts = df['ErrorCode'].value_counts()
                    ax.bar(counts.index, counts.values, color="#00796b")
                    ax.set_title("Histogramme des Erreurs")
                    ax.set_xlabel("Code d'erreur")
                    ax.set_ylabel("Occurrences")
                    ax.tick_params(axis='x', rotation=45)
                elif vis_type == "Courbe":
                    for code in error_counts.columns:
                        ax.plot(error_counts.index, error_counts[code], marker='o', label=code)
                    ax.set_title("Évolution des erreurs")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Occurrences")
                    ax.legend()
                    ax.tick_params(axis='x', rotation=45)

                st.pyplot(fig)
                st.subheader("📅 Nombre d'erreurs par date et code")
                st.dataframe(error_counts.style.highlight_max(axis=0))

                st.subheader("📌 Répartition globale")
                st.write(df['ErrorCode'].value_counts())

            csv = df.to_csv(index=False)
            st.download_button("📅 Télécharger les erreurs en CSV", csv, "erreurs_extraites.csv", mime="text/csv")
        else:
            st.error("⚠️ Aucun log valide détecté.")
