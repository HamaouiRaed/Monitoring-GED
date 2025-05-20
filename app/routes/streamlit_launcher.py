import subprocess
import time

def run_streamlit():
    """Launch the Streamlit dashboard in a separate process."""
    try:
        subprocess.Popen([
            "streamlit", "run", "app/controllers/streamlit_app.py", "--server.port=8501"
        ])
        time.sleep(3)  # Allow time for the server to start
    except Exception as e:
        print(f"Erreur lors du lancement de Streamlit : {e}")
