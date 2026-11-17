"""Live integration checks using the user's authenticated Codex CLI."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.codex_client import answer_with_codex
from src.retrieve import KnowledgeBase


def main():
    kb = KnowledgeBase()
    tests = [
        ("什么是最便宜可交割债券（CTD）？", False),
        ("LTCM 为什么会陷入流动性危机？", False),
        ("请告诉我明天纽约的天气和准确温度。", True),
    ]
    checks = []
    for question, insufficient in tests:
        sources = kb.search(question, top_k=8)
        result = answer_with_codex(question, sources)
        if insufficient:
            assert result["insufficient_evidence"] and not result["citations"], result
        else:
            # A sourced partial answer may honestly flag incomplete evidence.
            assert result["citations"], result
        checks.append({"question": question, **result})
        print(f"PASS: {question}", flush=True)
    (ROOT / "tmp" / "live-answers.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")

    # This uses the registered global MCP configuration, as a fresh Codex session would.
    command = [shutil.which("codex"), "exec", "--ephemeral", "--skip-git-repo-check",
               "--sandbox", "read-only", "--json", "-",
               ]
    prompt = ("只使用 books-rag MCP 工具，不使用 shell 或其他工具。先调用 list_books，"
              "再调用 search_books 检索 cheapest to deliver bond，top_k=3。"
              "用中文两句话说明最便宜可交割债券是什么，引用书名与 PDF 物理页码。")
    process = subprocess.run(command, input=prompt, encoding="utf-8", errors="replace",
                             capture_output=True, cwd=ROOT, timeout=180,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if process.returncode:
        raise RuntimeError("Fresh Codex MCP session failed; inspect local diagnostics.")
    events = []
    for line in process.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    calls = [e["item"] for e in events if e.get("type") == "item.completed"
             and e.get("item", {}).get("type") == "mcp_tool_call"]
    names = {c.get("tool") for c in calls if c.get("status") == "completed"}
    (ROOT / "tmp" / "codex-mcp-events.json").write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    assert {"list_books", "search_books"}.issubset(names), names
    print("PASS: Fresh Codex session called registered books-rag MCP tools", flush=True)


if __name__ == "__main__":
    main()
