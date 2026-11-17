"""UI translations. Widget values stay stable across languages."""

UI = {
    "en": {
        "subtitle": "Treasury basis & risk management · Your two-book research assistant",
        "welcome": "Welcome! I can help you explore US Treasury cash and futures markets, basis and delivery, arbitrage, and leverage, liquidity and risk management through the LTCM story. Ask a question and I will show the book passages behind the answer.",
        "scope": "Sources: The Treasury Bond Basis and When Genius Failed (Chinese edition). These are historical books. Citations use physical PDF page numbers.",
        "not_ready": "The knowledge base is not ready. Run the setup cell in Start_RAG.ipynb, or run: python -m src.ingest",
        "shelf": "Your knowledge shelf", "book_stats": "{pages} pages · {chunks:,} passages",
        "ocr_pages": "{count} pages supplemented with OCR", "range": "Search scope", "all": "All books",
        "mode": "Mode", "answer_mode": "Ask Codex", "search_mode": "Search passages only",
        "top_k": "Passages to retrieve", "privacy": "Embedding and FAISS search run locally. In Ask Codex mode, your question and retrieved passages are sent to Codex.",
        "cli_ready": "Codex CLI found", "cli_missing": "Codex CLI not found. Passage search is still available.",
        "sources": "Sources", "books": "{count} books", "passages": "Traceable passages", "vectors": "Vector search",
        "dimensions": "FAISS · {count}D", "start": "Start with a question",
        "examples": ["What is the cheapest-to-deliver bond (CTD)?", "Why did LTCM face a liquidity crisis?", "How do financing costs affect a basis trade?"],
        "question": "Your question", "placeholder": "Ask in English or Chinese. Answers include references to the books…",
        "submit": "Search and answer", "empty": "Please enter a question first.", "searching": "Searching the books…",
        "answering": "Codex is preparing an answer from the retrieved evidence…", "asked": "Question",
        "partial": "The retrieved evidence is incomplete. Try a more specific question or select one book.",
        "evidence": "Source passages", "score_note": "Similarity is a retrieval score, not a probability that an answer is correct. Check the original PDF for formulas and tables.",
        "source_label": "[{citation}] {title} · PDF p. {page} · similarity {score:.3f}",
        "ocr_note": "OCR transcription: check the original PDF, especially numbers and formulas.", "chunk": "Passage ID",
        "language_note": "New answers follow the selected language. Original passages keep their original language.",
        "answer_language": "Answer language", "error": "The request failed. Please check the knowledge base and Codex login, then retry.",
    },
    "zh": {
        "subtitle": "国债基差与风险管理 · 双书阅读助手",
        "welcome": "欢迎！我的知识领域是美国国债现货与期货、基差与交割、套利交易，以及 LTCM 案例中的杠杆、流动性与风险管理。你可以询问概念、交易机制或两本书的观点，我会给出原文出处。",
        "scope": "知识来源：《The Treasury Bond Basis》与《赌金者》。书籍内容为历史资料；引用页码为 PDF 物理页码。",
        "not_ready": "知识库尚未就绪。请运行 Start_RAG.ipynb 的准备单元格，或运行：python -m src.ingest",
        "shelf": "你的知识书架", "book_stats": "{pages} 页 · {chunks:,} 个片段", "ocr_pages": "其中 {count} 页使用 OCR 补充提取",
        "range": "检索范围", "all": "全部书籍", "mode": "使用方式", "answer_mode": "Codex 问答", "search_mode": "仅检索原文",
        "top_k": "召回片段数", "privacy": "Embedding 与 FAISS 检索在本地运行。使用 Codex 问答时，问题和召回片段会发送给 Codex。",
        "cli_ready": "已找到 Codex CLI", "cli_missing": "未找到 Codex CLI，可先使用检索模式。",
        "sources": "知识来源", "books": "{count} 本书", "passages": "可追溯片段", "vectors": "向量检索", "dimensions": "FAISS · {count} 维",
        "start": "从一个问题开始", "examples": ["什么是最便宜可交割债券（CTD）？", "LTCM 为什么会陷入流动性危机？", "基差交易中的融资成本如何影响收益？"],
        "question": "你的问题", "placeholder": "输入中英文问题，回答会附上书籍原文依据……", "submit": "检索并回答",
        "empty": "请先输入一个问题。", "searching": "正在检索书籍原文……", "answering": "Codex 正在根据检索证据组织回答……",
        "asked": "问题", "partial": "本次检索证据不完整，可改写问题或缩小到一本书。", "evidence": "原文依据",
        "score_note": "相似度表示检索匹配程度，不代表答案正确概率。公式和表格可能无法完整提取，请核对原 PDF。",
        "source_label": "[{citation}] {title} · PDF 第 {page} 页 · 相似度 {score:.3f}",
        "ocr_note": "本片段由 OCR 识别，请核对原 PDF，尤其是数字与公式。", "chunk": "片段 ID",
        "language_note": "新回答使用所选语言；原文片段保留书籍本来的语言。", "answer_language": "回答语言",
        "error": "请求失败，请检查知识库及 Codex 登录状态后重试。",
    },
}

ERRORS_EN = {
    "请输入问题。": "Please enter a question.",
    "问题请控制在 2000 字符以内。": "Please limit your question to 2,000 characters.",
    "未知的 book_id。": "Unknown book. Please select another search scope.",
    "未找到 Codex CLI。安装并执行 codex login 后重试；仍可使用仅检索模式。": "Codex CLI was not found. Install it and run codex login, or use passage search.",
    "Codex 回答超时，请稍后重试。检索结果已保留。": "Codex timed out. Please retry later. Your source passages are still available.",
    "Codex 调用失败。请在终端运行 codex login status 检查登录及网络后重试。": "Codex failed. Run codex login status in a terminal and check your connection, then retry.",
    "Codex 未返回有效的结构化回答，请重试。": "Codex did not return a valid structured answer. Please retry.",
    "Codex 返回格式不正确。": "Codex returned an invalid response format.",
    "回答出现不存在的来源编号，请重试。": "The answer cited an unknown source. Please retry.",
    "回答正文与来源列表不一致，请重试。": "The answer and source list do not match. Please retry.",
    "回答缺少来源引用，请重试。": "The answer is missing source citations. Please retry.",
}


def error_message(message, language):
    return message if language == "zh" else ERRORS_EN.get(message, UI["en"]["error"])


def display_title(title, language):
    if language == "en" and "赌金者" in title:
        return "When Genius Failed (Chinese edition)"
    return title
