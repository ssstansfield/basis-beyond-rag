import json
import re
import subprocess
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.embedding import tokenizer
from src.ingest import split_text, clean_text
from src.retrieve import KnowledgeBase
from src.settings import ROOT, CHUNK_TOKENS
from src import codex_client


def test_chunking_preserves_text_and_respects_real_tokenizer():
    tok = tokenizer()
    for text in ["国债期货交割时需要考虑转换因子和融资成本。" * 45,
                 "The cheapest to deliver bond depends on carry and conversion factors. " * 60]:
        parts = list(split_text(text, tok))
        assert len(parts) > 1
        assert all(len(tok.encode(p, add_special_tokens=False).ids) <= CHUNK_TOKENS for p in parts)
        assert parts[0].startswith(text[:20])
        assert parts[-1].endswith(text.strip()[-20:])
    assert clean_text("123\nHeader\n债券\n交割", {"Header"}) == "债券交割"


def test_retrieval_real_books_and_filters():
    kb = KnowledgeBase()
    assert len(kb.manifest["books"]) == 2
    treasury = next(b for b in kb.manifest["books"] if "Treasury" in b["title"])
    ltcm = next(b for b in kb.manifest["books"] if "赌金者" in b["title"])
    results = kb.search("What is the cheapest to deliver bond?", treasury["book_id"])
    assert all(r["book_id"] == treasury["book_id"] for r in results)
    assert any("cheapest" in r["text"].lower() for r in results)
    results = kb.search("长期资本管理公司为什么在危机中无法平仓，流动性和杠杆有什么关系？", ltcm["book_id"])
    assert all(r["book_id"] == ltcm["book_id"] for r in results)
    assert any(any(t in r["text"] for t in ["杠杆", "流动", "平仓"]) for r in results)
    assert kb.get_chunk(results[0]["chunk_id"])["text"] == results[0]["text"]
    with pytest.raises(ValueError):
        kb.search(" ")
    with pytest.raises(ValueError):
        kb.search("basis", "nonexistent")


def test_rejects_fabricated_citation(monkeypatch):
    monkeypatch.setattr(codex_client.shutil, "which", lambda _: "codex")
    def fake_run(command, **kwargs):
        Path(command[command.index("-o") + 1]).write_text(json.dumps({
            "answer": "Invented [S99]", "citations": ["S99"], "insufficient_evidence": False}), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(codex_client.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="不存在"):
        codex_client.answer_with_codex("test", [{"citation": "S1", "text": "source"}])


def test_ui_retrieval_flow():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=45).run()
    assert not app.exception
    assert app.title[0].value == "Basis & Beyond"
    assert app.selectbox(key="language").value == "en"
    assert app.text_area[0].label == "Your question"
    app.radio[0].set_value("search")
    app.text_area[0].set_value("What is the cheapest to deliver bond?")
    app.button[-1].click().run()
    assert not app.exception
    assert len(app.expander) > 0
    assert "PDF p." in app.expander[0].label
    # Changing language preserves the question and retrieved results.
    app.selectbox(key="language").set_value("zh").run()
    assert not app.exception
    assert app.text_area[0].label == "你的问题"
    assert app.text_area[0].value == "What is the cheapest to deliver bond?"
    assert "PDF 第" in app.expander[0].label
    assert app.radio[0].value == "search"


def test_answer_language_follows_ui(monkeypatch):
    monkeypatch.setattr(codex_client.shutil, "which", lambda _: "codex")
    captured = []
    def fake_run(command, **kwargs):
        captured.append(kwargs["input"])
        Path(command[command.index("-o") + 1]).write_text(json.dumps({
            "answer": "Evidence [S1]", "citations": ["S1"], "insufficient_evidence": False}), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(codex_client.subprocess, "run", fake_run)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=45).run()
    app.text_area[0].set_value("What is CTD?")
    app.button[-1].click().run()
    assert not app.exception
    assert "回答语言：English" in captured[-1]
    app.selectbox(key="language").set_value("zh").run()
    app.button[-1].click().run()
    assert not app.exception
    assert "回答语言：中文" in captured[-1]
