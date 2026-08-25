# src/app.py
import streamlit as st
import time
import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AuditScribe",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AuditScribe — A self-correcting RAG documentation engine."
    }
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --ink:        #0f1117;
    --ink-2:      #3d4252;
    --ink-3:      #7c8295;
    --surface:    #f7f8fa;
    --card:       #ffffff;
    --border:     #e4e6ec;
    --accent:     #f0a500;
    --accent-dim: rgba(240,165,0,0.12);
    --green:      #16a34a;
    --green-dim:  rgba(22,163,74,0.1);
    --red:        #dc2626;
    --sb-bg:      #0f1117;
    --sb-surface: #191c27;
    --sb-border:  #262a38;
    --sb-text:    #a8afc4;
    --sb-text-hi: #e8eaf2;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
}

.block-container {
    padding: 2rem 2.5rem 8rem !important;
    max-width: 960px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
}
[data-testid="stSidebar"] * { color: var(--sb-text) !important; }
[data-testid="stSidebar"] .block-container { padding: 1.6rem 1.4rem 2rem !important; }
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid var(--sb-border) !important;
    margin: 1.2rem 0 !important;
}
.sb-brand {
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--sb-text-hi) !important;
    letter-spacing: -0.02em;
    line-height: 1;
}
.sb-brand em { font-style: normal; color: var(--accent) !important; }
.sb-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-top: 5px;
    margin-bottom: 1.4rem;
}
.sb-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-3) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
}
.sb-metric {
    background: var(--sb-surface);
    border: 1px solid var(--sb-border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}
.sb-metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: var(--ink-3) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.sb-metric-value {
    font-weight: 700;
    font-size: 1.6rem;
    line-height: 1;
    color: var(--sb-text-hi) !important;
}
.sb-metric-value.good { color: #22c55e !important; }
.sb-metric-value.warn { color: var(--accent) !important; }
.sb-metric-value.bad  { color: var(--red) !important; }

[data-testid="stSidebar"] .stButton > button {
    background: var(--sb-surface) !important;
    color: var(--sb-text-hi) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    transition: border-color 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: var(--sb-surface) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 7px !important;
    color: var(--sb-text-hi) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--sb-border) !important;
}
[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] {
    color: var(--ink-3) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--sb-surface) !important;
    border: 1px dashed var(--sb-border) !important;
    border-radius: 7px !important;
}
.log-line {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--ink-3) !important;
    padding: 5px 0;
    border-bottom: 1px solid var(--sb-border);
}
.sb-stack {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: var(--sb-border) !important;
    line-height: 2;
}

/* ── Hero ── */
.hero { padding: 0.5rem 0 1.5rem; }
.hero-title {
    font-weight: 700;
    font-size: 2.4rem;
    letter-spacing: -0.03em;
    color: var(--ink);
    line-height: 1;
    margin: 0;
}
.hero-title em { font-style: normal; color: var(--accent); }
.hero-desc {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.6rem;
}

/* ── Message bubbles — NO icons ── */
.msg-user {
    background: var(--accent-dim);
    border: 1.5px solid var(--accent);
    border-radius: 12px;
    padding: 0.75rem 1.2rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.95rem;
    color: var(--ink);
}

.msg-assistant {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.5rem;
    color: var(--ink);
    font-size: 0.95rem;
    line-height: 1.7;
}

/* Source badge */
.source-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.6rem;
}
.source-badge.docs {
    background: var(--green-dim);
    color: var(--green);
    border: 1px solid rgba(22,163,74,0.2);
}
.source-badge.web {
    background: rgba(240,165,0,0.1);
    color: #b45309;
    border: 1px solid rgba(240,165,0,0.3);
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--ink-3) !important;
}

/* ── Suggestion buttons ── */
.suggest-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.2rem 0 0.5rem;
}
.stButton > button {
    background: var(--card) !important;
    color: var(--ink-2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 0.8rem !important;
    text-align: left !important;
    transition: border-color 0.15s, background 0.15s !important;
    white-space: normal !important;
    height: auto !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    background: var(--accent-dim) !important;
    color: var(--ink) !important;
}

/* ── Score bars ── */
.scores-wrap {
    margin-top: 0.8rem;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.3rem;
}
.scores-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
}
.score-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.55rem;
}
.score-row:last-child { margin-bottom: 0; }
.score-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--ink-3);
    width: 130px;
    flex-shrink: 0;
}
.score-track {
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
}
.score-fill { height: 100%; border-radius: 3px; }
.score-num {
    font-weight: 700;
    font-size: 0.85rem;
    width: 36px;
    text-align: right;
}

.stAlert {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
.stSpinner > div { border-top-color: var(--accent) !important; }
.stCaption { color: var(--ink-3) !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("faith_score", None), ("rel_score", None),
    ("latency", None), ("report", None),
    ("ingest_log", []),
    ("messages", []),
    ("suggestions", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_cls(v):
    if v is None: return ""
    return "good" if v >= 0.75 else ("warn" if v >= 0.5 else "bad")

def fmt(v):
    return f"{v:.2f}" if v is not None else "—"

def bar_color(v):
    if v >= 0.75: return "#16a34a"
    if v >= 0.5:  return "#f0a500"
    return "#dc2626"

def scores_html(f, r):
    return f"""
    <div class="scores-wrap">
        <div class="scores-title">Quality Scores</div>
        <div class="score-row">
            <div class="score-name">Faithfulness</div>
            <div class="score-track"><div class="score-fill" style="width:{f*100:.0f}%;background:{bar_color(f)};"></div></div>
            <div class="score-num" style="color:{bar_color(f)}">{f:.2f}</div>
        </div>
        <div class="score-row">
            <div class="score-name">Answer Relevancy</div>
            <div class="score-track"><div class="score-fill" style="width:{r*100:.0f}%;background:{bar_color(r)};"></div></div>
            <div class="score-num" style="color:{bar_color(r)}">{r:.2f}</div>
        </div>
    </div>"""

def source_badge(source):
    if source == "web":
        return '<div class="source-badge web">⚠ Web Search — no matching content found in your documents</div>'
    return '<div class="source-badge docs">✦ Answered from your documents</div>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-brand">Audit<em>Scribe</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Self-Correcting RAG Engine</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Last Run</div>', unsafe_allow_html=True)
    for label, val in [
        ("Faithfulness",     st.session_state.faith_score),
        ("Answer Relevancy", st.session_state.rel_score),
    ]:
        cls = score_cls(val)
        st.markdown(f"""
        <div class="sb-metric">
            <div class="sb-metric-label">{label}</div>
            <div class="sb-metric-value {cls}">{fmt(val)}</div>
        </div>""", unsafe_allow_html=True)

    lat = st.session_state.latency
    st.markdown(f"""
    <div class="sb-metric">
        <div class="sb-metric-label">Latency</div>
        <div class="sb-metric-value">{f"{lat}s" if lat else "—"}</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sb-label">Knowledge Base</div>', unsafe_allow_html=True)
    tab_pdf, tab_url = st.tabs(["PDF", "URL"])

    with tab_pdf:
        uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
        if st.button("Ingest PDF", key="ingest_pdf_btn", use_container_width=True):
            if uploaded_file:
                with st.spinner("Chunking & embedding…"):
                    res = requests.post(
                        f"{API_URL}/ingest/pdf",
                        files={"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
                    )
                    data = res.json()
                st.success(f"✓ {data['chunks']} chunks added")
                st.session_state.ingest_log.append(
                    f"PDF · {uploaded_file.name} · {data['chunks']} chunks"
                )
            else:
                st.warning("Upload a PDF first.")

    with tab_url:
        url_input = st.text_input("URL", placeholder="https://docs.example.com", label_visibility="collapsed")
        if st.button("Ingest URL", key="ingest_url_btn", use_container_width=True):
            if url_input.startswith("http"):
                with st.spinner("Scraping & embedding…"):
                    res = requests.post(f"{API_URL}/ingest/url", params={"url": url_input})
                    data = res.json()
                st.success(f"✓ {data['chunks']} chunks added")
                st.session_state.ingest_log.append(
                    f"URL · {url_input[:40]}… · {data['chunks']} chunks"
                )
            else:
                st.warning("Enter a valid URL.")

    if st.session_state.ingest_log:
        st.divider()
        st.markdown('<div class="sb-label">Ingestion Log</div>', unsafe_allow_html=True)
        for entry in st.session_state.ingest_log[-6:]:
            st.markdown(f'<div class="log-line">✓ {entry}</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.suggestions = []
        st.session_state.report = None
        st.session_state.faith_score = None
        st.session_state.rel_score = None
        st.session_state.latency = None
        st.rerun()

    st.divider()
    st.markdown("""
    <div class="sb-stack">
    Groq · gpt-oss-120b / gpt-oss-20b<br>
    LangGraph · CrewAI<br>
    Ragas · bge-large-en-v1.5<br>
    ChromaDB · Streamlit
    </div>""", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Audit<em>Scribe</em></div>
    <div class="hero-desc">Retrieve · Verify · Score · Deliver</div>
</div>
""", unsafe_allow_html=True)

# ── Render existing chat history — NO icons ────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="msg-assistant">', unsafe_allow_html=True)
        # Source badge
        if "source" in msg:
            st.markdown(source_badge(msg["source"]), unsafe_allow_html=True)
        st.markdown(msg["content"])
        # Scores
        if "faith" in msg:
            st.markdown(scores_html(msg["faith"], msg["rel"]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Suggestion buttons ────────────────────────────────────────────────────────
if st.session_state.suggestions:
    st.markdown('<div class="suggest-label">You might also ask</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, suggestion in zip(cols, st.session_state.suggestions):
        with col:
            if st.button(suggestion, use_container_width=True, key=f"sug_{suggestion[:30]}"):
                st.session_state["_pending_query"] = suggestion
                st.session_state.suggestions = []
                st.rerun()


# ── Chat input — anchors to bottom automatically ──────────────────────────────
query = st.chat_input("Ask a question about your documents…")

if "_pending_query" in st.session_state:
    query = st.session_state.pop("_pending_query")


# ── Process query ─────────────────────────────────────────────────────────────
if query:
    # Show user message immediately
    st.markdown(
        f'<div class="msg-user">{query}</div>',
        unsafe_allow_html=True
    )
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("AuditScribe is thinking…"):
        start_time = time.time()
        try:
            res = requests.post(
                f"{API_URL}/audit/run",
                json={
                    "query": query,
                    "history": st.session_state.messages[:-1]
                }
            )
            if res.status_code != 200:
                try:
                    detail = res.json().get("detail", "Unknown error")
                except Exception:
                    detail = f"Server error {res.status_code} — check FastAPI terminal."
                st.error(f"API error: {detail}")
                st.stop()

            data = res.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
            st.stop()

    report_text  = data["report"]
    faith        = data.get("faithfulness", 0.0)
    rel          = data.get("answer_relevancy", 0.0)
    suggestions  = data.get("suggestions", [])
    source       = data.get("source", "docs")
    total_time   = round(data.get("latency", time.time() - start_time), 2)

    # Render assistant message — no icon
    st.markdown('<div class="msg-assistant">', unsafe_allow_html=True)
    st.markdown(source_badge(source), unsafe_allow_html=True)
    st.markdown(report_text)
    st.markdown(scores_html(faith, rel), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Status alert
    if faith >= 0.75 and rel >= 0.75:
        st.success("High-confidence answer — faithfulness and relevancy both passed.")
    elif faith < 0.5:
        st.error("Faithfulness is low — try ingesting a relevant document first.")
    elif rel < 0.5:
        st.warning("Relevancy is low — try rephrasing your question.")

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": report_text,
        "faith": faith,
        "rel": rel,
        "source": source,
    })
    st.session_state.faith_score = faith
    st.session_state.rel_score   = rel
    st.session_state.latency     = total_time
    st.session_state.report      = report_text
    st.session_state.suggestions = suggestions

    st.rerun()
