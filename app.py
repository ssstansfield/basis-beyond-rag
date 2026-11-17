import shutil

import streamlit as st

from src.codex_client import answer_with_codex
from src.i18n import UI, display_title, error_message
from src.retrieve import KnowledgeBase
from src.settings import DATA

st.set_page_config(page_title="Basis & Beyond", page_icon="📚", layout="wide")
# Inherit native colors: recent Streamlit versions do not expose legacy
# --text-color / --secondary-background-color variables to st.markdown.
# Leave page, sidebar, text and widget colors under Streamlit's control.
st.markdown("""<style>
.block-container {max-width: 1140px; padding-top: 2.8rem;}
h1 {letter-spacing: -.035em;}
[data-testid="stMetric"] {
    padding: 1rem; border-radius: 12px;
    border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
}
.eyebrow {color: inherit; font-size:.8rem; letter-spacing:.16em; font-weight:700;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    language = st.selectbox("Language / 语言", ["en", "zh"],
                            format_func=lambda value: {"en": "English", "zh": "中文"}[value], key="language")
t = UI[language]


@st.cache_resource
def load_kb(generation):
    return KnowledgeBase()


st.markdown('<div class="eyebrow">BOOKS / RESEARCH / EVIDENCE</div>', unsafe_allow_html=True)
st.title("Basis & Beyond")
st.subheader(t["subtitle"])
st.write(t["welcome"])
st.caption(t["scope"])

try:
    generation = (DATA / "CURRENT").read_text().strip()
    kb = load_kb(generation)
except (OSError, RuntimeError):
    st.info(t["not_ready"])
    st.stop()

with st.sidebar:
    st.header(t["shelf"])
    for b in kb.manifest["books"]:
        st.markdown(f"**{display_title(b['title'], language)}**")
        st.caption(t["book_stats"].format(**b))
        if b.get("ocr_pages"):
            st.caption(t["ocr_pages"].format(count=len(b["ocr_pages"])))
    st.divider()
    books = {b["book_id"]: b for b in kb.manifest["books"]}
    selection = st.selectbox(t["range"], ["all", *books], key="book_filter",
        format_func=lambda value: t["all"] if value == "all" else display_title(books[value]["title"], language))
    mode = st.radio(t["mode"], ["answer", "search"], key="mode",
                    format_func=lambda value: t["answer_mode"] if value == "answer" else t["search_mode"])
    k = st.slider(t["top_k"], 3, 12, 8, key="top_k")
    st.caption(t["privacy"])
    st.caption(t["cli_ready"] if shutil.which("codex") else t["cli_missing"])
    st.caption(t["language_note"])

cols = st.columns(3)
cols[0].metric(t["sources"], t["books"].format(count=len(books)))
cols[1].metric(t["passages"], f"{kb.manifest['chunks']:,}")
cols[2].metric(t["vectors"], t["dimensions"].format(count=kb.manifest["dimension"]))

st.write(t["start"])
buttons = st.columns(3)
for i, (col, example) in enumerate(zip(buttons, t["examples"])):
    if col.button(example, use_container_width=True, key=f"example_{i}"):
        st.session_state["question"] = example

with st.form("ask"):
    question = st.text_area(t["question"], key="question", placeholder=t["placeholder"], max_chars=2000, height=100)
    submitted = st.form_submit_button(t["submit"], type="primary")

if submitted:
    if not question.strip():
        st.warning(t["empty"])
    else:
        st.session_state.pop("result", None)
        try:
            with st.spinner(t["searching"]):
                sources = kb.search(question, None if selection == "all" else selection, k)
            record = {"question": question, "sources": sources, "answer": None, "error": None,
                      "mode": mode, "language": language}
            st.session_state["result"] = record
            if mode == "answer":
                with st.spinner(t["answering"]):
                    record["answer"] = answer_with_codex(question, sources, language=language)
        except (RuntimeError, ValueError, OSError) as exc:
            if "result" in st.session_state:
                st.session_state["result"]["error"] = str(exc)
            else:
                st.error(error_message(str(exc), language))

if "result" in st.session_state:
    record = st.session_state["result"]
    st.divider()
    st.markdown(f"**{t['asked']}:** {record['question']}")
    if record["error"]:
        st.error(error_message(record["error"], language))
    if record["answer"]:
        st.caption(f"{t['answer_language']}: {'English' if record['language'] == 'en' else '中文'}")
        st.markdown(record["answer"]["answer"])
        if record["answer"]["insufficient_evidence"]:
            st.info(t["partial"])
    st.subheader(t["evidence"])
    st.caption(t["score_note"])
    for s in record["sources"]:
        label = {**s, "title": display_title(s["title"], language)}
        with st.expander(t["source_label"].format(**label)):
            if s["chapter"]:
                st.caption(s["chapter"])
            st.text(s["text"])
            if s.get("extraction") == "ocr":
                st.caption(t["ocr_note"])
            st.caption(f"{t['chunk']}: {s['chunk_id']}")
