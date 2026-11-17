"""Run: python -m src.ingest [--force]. No book text is sent to a remote API."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import uuid

import faiss
import numpy as np
import pymupdf

from .embedding import embed, tokenizer
from .settings import ROOT, DATA, MODEL, CHUNK_TOKENS, OVERLAP, book_title

PIPELINE_VERSION = 2


def extract_pages(doc, file_hash):
    """Recover image-only pages locally; cache OCR by source hash and page."""
    pages, ocr_pages = [], []
    engine = None
    for i, page in enumerate(doc):
        text = page.get_text(sort=True)
        if len(text.strip()) < 80 and page.get_images():
            cache = DATA / "ocr" / file_hash / f"{i+1}.txt"
            if cache.exists():
                recovered = cache.read_text(encoding="utf-8")
            else:
                if engine is None:
                    from rapidocr_onnxruntime import RapidOCR
                    engine = RapidOCR(intra_op_num_threads=4, inter_op_num_threads=1)
                result, _ = engine(page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).tobytes("png"))
                recovered = "\n".join(line[1] for line in (result or []) if line[2] >= .5)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(recovered, encoding="utf-8")
                print(f"OCR PDF page {i+1}: {len(recovered)} characters", flush=True)
            if len(recovered.strip()) > len(text.strip()):
                text = recovered
                ocr_pages.append(i + 1)
        pages.append(text)
    return pages, ocr_pages


def clean_text(text, repeated=()):
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and line not in repeated and not re.fullmatch(r"\d+", line)]
    text = "\n".join(lines)
    text = re.sub(r"([A-Za-z])-\n([a-z])", r"\1\2", text)
    text = re.sub(r"(?<=[\u3400-\u9fff])\n(?=[\u3400-\u9fff])", "", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def split_text(text, tok, budget=CHUNK_TOKENS, overlap=OVERLAP):
    if not 0 <= overlap < budget:
        raise ValueError("overlap must be smaller than budget")
    offsets = tok.encode(text, add_special_tokens=False).offsets
    start = 0
    while start < len(offsets):
        end = min(start + budget, len(offsets))
        # Prefer sentence endings near the target while respecting the token cap.
        if end < len(offsets):
            for candidate in range(end, max(start + budget // 2, start + overlap + 1), -1):
                if text[offsets[candidate - 1][1] - 1] in ".!?。！？；;":
                    end = candidate
                    break
        piece = text[offsets[start][0]:offsets[end - 1][1]].strip()
        # Retokenizing at a substring boundary can change tokenization by a token.
        while len(tok.encode(piece, add_special_tokens=False).ids) > budget:
            end -= 1
            piece = text[offsets[start][0]:offsets[end - 1][1]].strip()
        if piece:
            yield piece
        if end == len(offsets):
            break
        start = max(start + 1, end - overlap)


def signature(files):
    return {"pipeline_version": PIPELINE_VERSION, "model": MODEL,
            "chunk_tokens": CHUNK_TOKENS, "overlap": OVERLAP,
            "sources": [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in files]}


def build(force=False):
    files = sorted((ROOT / "books").glob("*.pdf"))
    if not files:
        raise RuntimeError("books/ 中没有 PDF 文件。")
    DATA.mkdir(exist_ok=True)
    sig = signature(files)
    current = DATA / "CURRENT"
    if current.exists() and not force:
        old = json.loads((DATA / current.read_text().strip() / "manifest.json").read_text(encoding="utf-8"))
        if old["signature"] == sig:
            print("Sources unchanged; reusing existing index.", flush=True)
            return old

    tok = tokenizer()
    chunks, books = [], []
    for path in files:
        book_id = hashlib.sha256(path.name.encode()).hexdigest()[:12]
        title = book_title(path)
        with pymupdf.open(path) as doc:
            source = next(s for s in sig["sources"] if s["file"] == path.name)
            pages, ocr_pages = extract_pages(doc, source["sha256"])
            low_text = [i + 1 for i, text in enumerate(pages) if len(text.strip()) < 30]
            if len(low_text) > max(5, len(pages) * .15):
                raise RuntimeError(f"{title}: 大量页面无可提取正文，需要先做 OCR。")
            edges = Counter()
            for page in pages:
                lines = [x.strip() for x in page.splitlines() if x.strip()]
                edges.update(set(x for x in lines[:2] + lines[-2:] if len(x) < 100))
            repeated = {x for x, n in edges.items() if n >= max(5, len(pages) * .12)}
            toc = [(p, heading) for level, heading, p in doc.get_toc() if level <= 2]
            chapter = ""
            count_before = len(chunks)
            for page_no, raw in enumerate(pages, 1):
                for p, heading in toc:
                    if p == page_no:
                        chapter = heading
                text = clean_text(raw, repeated)
                match = re.search(r"(?:^|\n)(第[一二三四五六七八九十百\d]+章[^\n]{0,50})", text)
                if match:
                    chapter = match.group(1)
                for part, piece in enumerate(split_text(text, tok)):
                    if len(piece) < 25:
                        continue
                    chunks.append({"chunk_id": f"{book_id}-{page_no:04d}-{part:02d}",
                                   "book_id": book_id, "title": title, "file": path.name,
                                   "page": page_no, "chapter": chapter, "text": piece,
                                   "extraction": "ocr" if page_no in ocr_pages else "text"})
            books.append({"book_id": book_id, "title": title, "file": path.name,
                          "pages": len(pages), "chunks": len(chunks) - count_before,
                          "low_text_pages": low_text, "ocr_pages": ocr_pages})
            print(f"{title}: {len(pages)} pages, {books[-1]['chunks']} chunks", flush=True)
    if not chunks:
        raise RuntimeError("未提取到可索引的正文。")

    generation = "index-" + uuid.uuid4().hex[:12]
    target = DATA / generation
    target.mkdir()
    try:
        cached = {}
        if current.exists():
            previous = DATA / current.read_text().strip()
            previous_manifest = json.loads((previous / "manifest.json").read_text(encoding="utf-8"))
            if previous_manifest["signature"]["model"] == MODEL:
                old_index = faiss.read_index(str(previous / "vectors.faiss"))
                with sqlite3.connect(previous / "chunks.sqlite3") as db:
                    for row_id, text in db.execute("SELECT row_id, text FROM chunks"):
                        cached[text] = old_index.reconstruct(row_id)
        index = None
        for start in range(0, len(chunks), 128):
            texts = [c["text"] for c in chunks[start:start + 128]]
            missing = list(dict.fromkeys(t for t in texts if t not in cached))
            if missing:
                cached.update(zip(missing, embed(missing)))
            vectors = np.ascontiguousarray([cached[t] for t in texts], dtype="float32")
            if index is None:
                index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            print(f"Embedded {min(start + 128, len(chunks))}/{len(chunks)}", flush=True)
        faiss.write_index(index, str(target / "vectors.faiss"))
        with sqlite3.connect(target / "chunks.sqlite3") as db:
            db.execute("CREATE TABLE chunks (row_id INTEGER PRIMARY KEY, chunk_id TEXT UNIQUE, book_id TEXT, title TEXT, file TEXT, page INTEGER, chapter TEXT, text TEXT, extraction TEXT)")
            db.executemany("INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?)", [
                (i, c["chunk_id"], c["book_id"], c["title"], c["file"], c["page"], c["chapter"], c["text"], c["extraction"])
                for i, c in enumerate(chunks)])
            db.execute("CREATE INDEX book_idx ON chunks(book_id)")
        manifest = {"created_at": datetime.now(timezone.utc).isoformat(), "signature": sig,
                    "books": books, "chunks": len(chunks), "dimension": index.d,
                    "page_numbering": "PDF physical pages, 1-based; not printed book pages"}
        (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        # Readers retain their immutable generation until they reload.
        pointer = DATA / f"CURRENT.{uuid.uuid4().hex}.tmp"
        pointer.write_text(generation, encoding="utf-8")
        os.replace(pointer, current)
        return manifest
    except Exception:
        shutil.rmtree(target)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    print(json.dumps(build(parser.parse_args().force), ensure_ascii=False, indent=2))
