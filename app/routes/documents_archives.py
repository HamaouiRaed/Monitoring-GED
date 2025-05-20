import os
import re

# ✅ Fonction utilitaire : lit tous les fichiers journal fusion dans logs/
def get_total_documents_from_journal_dir(logs_dir):
    total_docs = 0
    for file in os.listdir(logs_dir):
        if file.lower().startswith("journal") and file.endswith((".log", ".txt")):
            path = os.path.join(logs_dir, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        match = re.search(r'Nombre total de fichiers traités\s*:\s*(\d+)', line)
                        if match:
                            total_docs += int(match.group(1))
            except Exception as e:
                print(f"[Erreur lecture] {file}: {e}")
    return total_docs
