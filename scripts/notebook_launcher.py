"""Standard-library-only bootstrap so any local Python kernel can launch the RAG."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import venv

ROOT = Path(__file__).resolve().parents[1]
_running = None


def runtime_python():
    return ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _run(command):
    subprocess.run([str(x) for x in command], cwd=ROOT, check=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def prepare():
    """Create the project runtime and restore/build the local knowledge base."""
    python = runtime_python()
    if not python.exists():
        if sys.version_info[:2] != (3, 12):
            raise RuntimeError("First setup requires a Python 3.12 notebook kernel. Please select Python 3.12 and retry.")
        print("Creating the project's Python environment…", flush=True)
        venv.EnvBuilder(with_pip=True).create(ROOT / ".venv")
    requirements = ROOT / "requirements.lock.txt"
    stamp = ROOT / ".venv" / ".rag-requirements-sha256"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    if not stamp.exists() or stamp.read_text() != digest:
        print("Checking/installing the application dependencies…", flush=True)
        uv = shutil.which("uv")
        if uv:
            _run([uv, "pip", "install", "--python", python, "-r", requirements])
        else:
            _run([python, "-m", "pip", "install", "-r", requirements])
        stamp.write_text(digest)
    data, bundled = ROOT / "data", ROOT / "knowledge"
    if not (data / "CURRENT").exists() and (bundled / "manifest.json").exists():
        destination = data / "index-bundled"
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("vectors.faiss", "chunks.sqlite3", "manifest.json"):
            shutil.copy2(bundled / name, destination / name)
        (data / "CURRENT").write_text(destination.name, encoding="utf-8")
        print("Restored the included two-book index.", flush=True)
    print("Checking the books and index…", flush=True)
    log = ROOT / "tmp" / "notebook-setup.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8") as output:
        process = subprocess.run([str(python), "-m", "src.ingest"], cwd=ROOT,
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                                 stdout=output, stderr=subprocess.STDOUT)
    if process.returncode:
        raise RuntimeError(f"Knowledge base setup failed. See {log}")
    print("Preparing the local multilingual embedding model (first run downloads it)…", flush=True)
    _run([python, "-c", "from src.embedding import model; model()"])
    return python


def healthy(url):
    try:
        with urllib.request.urlopen(url + "/_stcore/health", timeout=2) as response:
            return response.status == 200
    except OSError:
        return False


@dataclass
class RunningApp:
    process: subprocess.Popen
    url: str
    log: Path

    def stop(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        print("App stopped.")


def launch(port=8050, setup=True):
    """Repeated calls within a kernel reuse the same healthy process."""
    global _running
    if _running and _running.process.poll() is None and healthy(_running.url):
        print(f"App is already running: {_running.url}")
        return _running
    python = prepare() if setup else runtime_python()
    # Windows may reserve the preferred port; choose an available one if necessary.
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            probe.bind(("127.0.0.1", 0))
        selected_port = probe.getsockname()[1]
    url = f"http://127.0.0.1:{selected_port}"
    log = ROOT / "tmp" / "notebook-app.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen([
            str(python), "-m", "streamlit", "run", str(ROOT / "app.py"),
            "--server.address", "127.0.0.1", "--server.port", str(selected_port),
            "--server.headless", "true", "--browser.gatherUsageStats", "false"],
            cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError(f"App exited during startup. See {log}")
        if healthy(url):
            _running = RunningApp(process, url, log)
            print(f"Ready: {url}", flush=True)
            if not shutil.which("codex"):
                print("Codex CLI is not installed. Passage search works; install Codex and run codex login to enable answers.")
            return _running
        time.sleep(.5)
    process.terminate()
    process.wait(timeout=10)
    raise RuntimeError(f"App startup timed out. See {log}")
