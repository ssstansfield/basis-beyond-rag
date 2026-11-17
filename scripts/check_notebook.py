"""Execute the actual entry notebook, reuse its app, and stop the owned process."""
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
nb = nbformat.read(ROOT / "Start_RAG.ipynb", as_version=4)
nbformat.validate(nb)
nb.cells += [nbformat.v4.new_code_cell("""from scripts.notebook_launcher import healthy
assert healthy(rag.url)
same = launch()
assert same.process.pid == rag.process.pid
rag.stop()
assert rag.process.poll() is not None
print('Notebook startup, reuse and stop: PASS')""")]
client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
client.execute()
(ROOT / "tmp").mkdir(exist_ok=True)
nbformat.write(nb, ROOT / "tmp/notebook-executed.ipynb")
print("Notebook executed: PASS")
