"""Regenerate the clean, portable notebook entry point."""
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
}
nb.cells = [
    nbf.v4.new_markdown_cell("""# Basis & Beyond · Start your RAG

**Choose a Python 3.12 kernel, then select Run All.** The next cell prepares the environment, restores the included two-book knowledge base, downloads the local embedding model if needed, and opens the app below. After the first setup, it starts from the cached environment and index.

The interface defaults to **English**; switch to **中文** in the sidebar. Choose **Light / Dark / System** from Streamlit's **⋮ menu** in the top-right corner.

**Knowledge domain:** US Treasury cash and futures, basis, delivery and arbitrage; leverage, liquidity and risk management through the LTCM case. Sources: *The Treasury Bond Basis* and *When Genius Failed* (Chinese edition).

---
**使用方法：选择 Python 3.12 内核，然后点击「全部运行」。** 下方单元格自动准备环境与知识库并启动界面。首次使用需联网安装依赖和下载模型；后续复用本地缓存。界面默认英文，侧栏可切换中文；点击右上角 ⋮ 菜单中的 Light / Dark / System 切换主题。

Passage search runs locally. Answers require the Codex CLI: run `codex login` once in your terminal. When asking Codex, your question and retrieved passages are sent to Codex. Without Codex, choose **Search passages only**.

Keep this notebook with `app.py`, `scripts/`, `src/`, `books/` and `knowledge/` from the repository. Run Jupyter locally on the same machine as the browser."""),
    nbf.v4.new_code_cell("""from pathlib import Path
import sys
from IPython.display import display, HTML, IFrame

# Works from the repository root or a child directory in Jupyter / VS Code.
ROOT = next((p for p in (Path.cwd(), *Path.cwd().parents)
             if (p / 'app.py').is_file() and (p / 'scripts/notebook_launcher.py').is_file()), None)
if ROOT is None:
    raise RuntimeError('Open this notebook from the cloned RAG repository directory.')
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.notebook_launcher import launch
rag = launch()
display(HTML(f'<p><a href="{rag.url}" target="_blank">Open Basis &amp; Beyond / 在新标签页打开</a></p>'))
display(IFrame(src=rag.url, width='100%', height=900))"""),
    nbf.v4.new_markdown_cell("""## Reopen / stop · 重新打开或停止

Run the cell above again to reopen the same running app. To stop the process launched by this notebook, uncomment and run the next cell. If you restart the kernel without stopping the app, its process may keep running; the launcher selects another free port when needed.

重复运行上方单元格会复用同一应用进程。需要停止时，取消下一单元格的注释并运行。退出前建议先停止应用。"""),
    nbf.v4.new_code_cell("# rag.stop()"),
    nbf.v4.new_markdown_cell("""## Codex MCP (optional) · 在 Codex 中检索

The web UI works without MCP registration. To let Codex sessions search the same books directly, uncomment and run the following cell, then start a new Codex session. This registers `books-rag` using paths on your computer.

网页无需注册 MCP 即可使用。要让 Codex 会话直接检索两本书，取消下一单元格注释并运行，然后新建 Codex 会话。"""),
    nbf.v4.new_code_cell("""# import shutil, subprocess
# from scripts.notebook_launcher import runtime_python
# codex = shutil.which('codex')
# if not codex:
#     raise RuntimeError('Install Codex CLI and run codex login first.')
# subprocess.run([codex, 'mcp', 'add', 'books-rag', '--',
#                 str(runtime_python()), str(ROOT / 'mcp_entry.py')], check=True)"""),
]
nbf.validate(nb)
nbf.write(nb, ROOT / "Start_RAG.ipynb")
print("Created Start_RAG.ipynb (clean outputs, portable paths).")
