import json
import sqlite3

import faiss

from .embedding import embed
from .settings import DATA, MODEL


class KnowledgeBase:
    def __init__(self):
        pointer = DATA / "CURRENT"
        if not pointer.exists():
            raise RuntimeError("知识库尚未建立，请先运行 python -m src.ingest。")
        self.path = DATA / pointer.read_text().strip()
        self.manifest = json.loads((self.path / "manifest.json").read_text(encoding="utf-8"))
        if self.manifest["signature"]["model"] != MODEL:
            raise RuntimeError("Embedding 模型已变化，请重建索引。")
        self.index = faiss.read_index(str(self.path / "vectors.faiss"))
        with sqlite3.connect(self.path / "chunks.sqlite3") as db:
            db.row_factory = sqlite3.Row
            self.chunks = [dict(row) for row in db.execute("SELECT * FROM chunks ORDER BY row_id")]
        if self.index.ntotal != len(self.chunks):
            raise RuntimeError("向量索引与文本数量不一致，请重建。")
        self.by_id = {c["chunk_id"]: c for c in self.chunks}

    def search(self, query, book_id=None, top_k=6):
        if not query.strip():
            raise ValueError("请输入问题。")
        if len(query) > 2000:
            raise ValueError("问题请控制在 2000 字符以内。")
        if book_id and book_id not in {b["book_id"] for b in self.manifest["books"]}:
            raise ValueError("未知的 book_id。")
        top_k = max(1, min(int(top_k), 12))
        # Full search is cheap for two books and avoids post-filter starvation.
        scores, ids = self.index.search(embed([query]), self.index.ntotal)
        results, per_page = [], {}
        for score, row_id in zip(scores[0], ids[0]):
            c = self.chunks[int(row_id)]
            if book_id and c["book_id"] != book_id:
                continue
            key = (c["book_id"], c["page"])
            if per_page.get(key, 0) >= 2:
                continue
            per_page[key] = per_page.get(key, 0) + 1
            results.append({**c, "score": round(float(score), 4), "citation": f"S{len(results)+1}"})
            if len(results) == top_k:
                break
        return results

    def get_chunk(self, chunk_id):
        if chunk_id not in self.by_id:
            raise ValueError("未知的 chunk_id。")
        return self.by_id[chunk_id]
