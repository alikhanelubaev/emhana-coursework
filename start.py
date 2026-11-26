"""Терминалда python start.py: серверді іске қосып, браузерді ашады."""
import importlib.util
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen
import webbrowser


def open_when_ready(process):
    for _ in range(100):
        if process.poll() is not None:return
        try:
            with urlopen("http://127.0.0.1:8501/_stcore/health",timeout=1) as response:
                if response.status==200:
                    webbrowser.open("http://localhost:8501")
                    return
        except OSError:
            time.sleep(.3)


def main():
    if importlib.util.find_spec("streamlit") is None:
        print("Streamlit орнатылмаған. Алдымен: python -m pip install -r requirements.txt")
        return 1
    with socket.socket() as probe:
        try:probe.bind(("127.0.0.1",8501))
        except OSError:
            print("8501 порты бос емес. Бұрын ашылған Streamlit серверін Ctrl+C арқылы тоқтатыңыз.")
            return 1
    project=Path(__file__).resolve().parent
    process=subprocess.Popen([sys.executable,"-m","streamlit","run",str(project/"app.py"),"--server.address=127.0.0.1","--server.port=8501"],cwd=project)
    threading.Thread(target=open_when_ready,args=(process,),daemon=True).start()
    try:return process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait(timeout=10)
        return 0


if __name__=="__main__":
    raise SystemExit(main())
