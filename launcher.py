import threading
import subprocess
import time
import webview

def start_streamlit():
    subprocess.Popen(["streamlit", "run", "app.py"])

threading.Thread(target=start_streamlit).start()

time.sleep(5)

webview.create_window(
    "Student Career Intelligence System",
    "http://localhost:8501"
)

webview.start()
