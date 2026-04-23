import streamlit as st
import time
import os
import tempfile
from main import run_sentinel
from ingest import ingest_pdf, ingest_url

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

/* ── Design Tokens ── */
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
    --red-dim:    rgba(220,38,38,0.1);
    --yellow-dim: rgba(240,165,0,0.1);

    /* Sidebar */
    --sb-bg:      #0f1117;
    --sb-surface: #191c27;
    --sb-border:  #262a38;
    --sb-text:    #a8afc4;
    --sb-text-hi: #e8eaf2;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
}

.block-container {
    padding: 2rem 2.5rem 5rem !important;
    max-width: 960px !important;
}

/* ── Sidebar Shell ── */
[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--sb-text) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.6rem 1.4rem 2rem !important;
}
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid var(--sb-border) !important;
    margin: 1.2rem 0 !important;
}

/* ── Sidebar Brand ── */
.sb-brand {
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--sb-text-hi) !important;
    letter-spacing: -0.02em;
    line-height: 1;
}
.sb-brand em {
    font-style: normal;
    color: var(--accent) !important;
}
.sb-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #ffffff !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-top: 5px;
    margin-bottom: 1.4rem;
}

/* ── Metric Cards ── */
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

/* ── Sidebar Section Label ── */
.sb-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-3) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
}

/* ── Sidebar Buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: var(--sb-surface) !important;
    color: var(--sb-text-hi) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    transition: border-color 0.15s, background 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important;
    background: rgba(240,165,0,0.06) !important;
}

/* ── Sidebar Inputs ── */
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: var(--sb-surface) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 7px !important;
    color: var(--sb-text-hi) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
    color: var(--ink-3) !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}

/* ── Sidebar Tabs ── */
[data-testid="stSidebar"] .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--sb-border) !important;
    gap: 0 !important;
}
[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] {
    color: var(--ink-3) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.4rem 0.8rem !important;
}
[data-testid="stSidebar"] .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── Ingest Log ── */
.log-line {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--ink-3) !important;
    padding: 5px 0;
    border-bottom: 1px solid var(--sb-border);
}
.log-line:last-child { border-bottom: none; }

/* ── Stack Footer ── */
.sb-stack {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: var(--sb-border) !important;
    line-height: 2;
}

/* ── Main Hero ── */
.hero {
    padding: 0.5rem 0 2rem;
}
.hero-title {
    font-weight: 700;
    font-size: 2.4rem;
    letter-spacing: -0.03em;
    color: var(--ink);
    line-height: 1;
    margin: 0;
}
.hero-title em {
    font-style: normal;
    color: var(--accent);
}
.hero-desc {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.6rem;
}

/* ── Main Query Input ── */
.stTextInput > div > div > input {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--ink-3) !important;
}
.stTextInput label {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: var(--ink-2) !important;
}

/* ── Run Button ── */
.stButton > button {
    background: var(--accent) !important;
    color: var(--ink) !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: opacity 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Pipeline Steps ── */
.step {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.4rem;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 10px;
}
.step.active {
    border-color: var(--accent);
    background: var(--accent-dim);
}
.step.done {
    border-color: var(--green);
    background: var(--green-dim);
}
.step.waiting { opacity: 0.35; }
.step-icon { font-size: 1.1rem; margin-top: 1px; }
.step-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--ink);
    margin-bottom: 2px;
}
.step-detail {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--ink-3);
}

/* ── Result Panel ── */
.result-wrap {
    margin-top: 2rem;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}
.result-head {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.9rem 1.3rem;
    background: var(--ink);
    border-bottom: none;
}
.result-head-label {
    font-weight: 600;
    font-size: 0.82rem;
    color: #e8eaf2;
    letter-spacing: 0.02em;
}
.result-head-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
}
.result-body {
    padding: 1.6rem 1.8rem;
    font-size: 0.95rem;
    line-height: 1.7;
    color: var(--ink);
}
.result-body h1, .result-body h2, .result-body h3 {
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
}
.result-body code {
    background: #f1f3f8;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82em;
    padding: 0.1em 0.4em;
    color: var(--ink-2);
}

/* ── Score Bars ── */
.scores-wrap {
    margin-top: 1rem;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
}
.scores-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 1rem;
}
.score-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.65rem;
}
.score-row:last-child { margin-bottom: 0; }
.score-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
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

/* ── Alert overrides ── */
.stAlert {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── File uploader ── */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--sb-surface) !important;
    border: 1px dashed var(--sb-border) !important;
    border-radius: 7px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Caption ── */
.stCaption { color: var(--ink-3) !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("faith_score", None), ("rel_score", None),
    ("latency", None), ("report", None), ("ingest_log", []), ("history", [])
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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-brand">Audit<em>Scribe</em></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Self-Correcting RAG Engine</div>', unsafe_allow_html=True)

    # Metrics
    st.markdown('<div class="sb-label">Last Run</div>', unsafe_allow_html=True)

    for label, val in [
        ("Faithfulness", st.session_state.faith_score),
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

    # Knowledge base
    st.markdown('<div class="sb-label">Knowledge Base</div>', unsafe_allow_html=True)
    tab_pdf, tab_url = st.tabs(["PDF", "URL"])

    with tab_pdf:
        uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
        if st.button("Ingest PDF", key="ingest_pdf_btn", use_container_width=True):
            if uploaded_file:
                with st.spinner("Chunking & embedding…"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    n = ingest_pdf(tmp_path)
                    os.unlink(tmp_path)
                st.success(f"✓ {n} chunks added")
                st.session_state.ingest_log.append(f"PDF · {uploaded_file.name} · {n} chunks")
            else:
                st.warning("Upload a PDF first.")

    with tab_url:
        url_input = st.text_input("URL", placeholder="https://docs.example.com", label_visibility="collapsed")
        if st.button("Ingest URL", key="ingest_url_btn", use_container_width=True):
            if url_input.startswith("http"):
                with st.spinner("Scraping & embedding…"):
                    n = ingest_url(url_input)
                st.success(f"✓ {n} chunks added")
                st.session_state.ingest_log.append(f"URL · {url_input[:40]}… · {n} chunks")
            else:
                st.warning("Enter a valid URL.")

    if st.session_state.ingest_log:
        st.divider()
        st.markdown('<div class="sb-label">Ingestion Log</div>', unsafe_allow_html=True)
        for entry in st.session_state.ingest_log[-6:]:
            st.markdown(f'<div class="log-line">✓ {entry}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div class="sb-stack">
    Groq · llama-3.1-8b-instant<br>
    LangGraph · CrewAI<br>
    Ragas · bge-large-en-v1.5<br>
    ChromaDB · Streamlit
    </div>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Audit<em>Scribe</em></div>
    <div class="hero-desc">Retrieve · Verify · Score · Deliver</div>
</div>
""", unsafe_allow_html=True)

query = st.text_input(
    "Question",
    placeholder="e.g. How do I implement a circuit breaker in FastAPI?",
    label_visibility="visible"
)

col_btn, col_tip = st.columns([2, 8])
with col_btn:
    run_btn = st.button("Run AuditScribe", use_container_width=True)
with col_tip:
    st.caption("Ingest a relevant PDF or URL in the sidebar before running for best results.")


# ── Pipeline execution ─────────────────────────────────────────────────────────
if run_btn:
    if not query.strip():
        st.warning("Please enter a question first.")
    else:
        start_time = time.time()
        pipeline_ph = st.empty()

        STEPS = [
            ("🔍", "Retrieving Context",   "LangGraph · bge-large-en-v1.5 vector search · Tavily fallback"),
            ("⚖️", "Multi-Agent Audit",     "Critic validates accuracy · Writer formats output"),
            ("📊", "Evaluating Quality",    "Ragas · Faithfulness + Relevancy scoring"),
        ]

        def show_pipeline(active_step: int):
            html = ""
            for i, (icon, title, detail) in enumerate(STEPS):
                if i < active_step:
                    cls, ico = "done", "✓"
                elif i == active_step:
                    cls, ico = "active", icon
                else:
                    cls, ico = "waiting", icon
                html += f"""
                <div class="step {cls}">
                    <div class="step-icon">{ico}</div>
                    <div>
                        <div class="step-title">{title}</div>
                        <div class="step-detail">{detail}</div>
                    </div>
                </div>"""
            pipeline_ph.markdown(html, unsafe_allow_html=True)

        show_pipeline(0)
        report, scores = run_sentinel(query)
        show_pipeline(1)
        time.sleep(0.2)
        show_pipeline(2)
        time.sleep(0.2)
        show_pipeline(3)

        total_time = round(time.time() - start_time, 2)

        st.session_state.history.append({
            "question": query,
            "report": report,
            "faith": float(scores.get("faithfulness", 0.0)),
            "rel": float(scores.get("answer_relevancy", 0.0)),
            "latency": total_time,
        })

        st.session_state.faith_score = float(scores.get("faithfulness", 0.0))
        st.session_state.rel_score   = float(scores.get("answer_relevancy", 0.0))
        st.session_state.latency     = total_time
        st.session_state.report      = report

        st.rerun()

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[:-1])):  # all but latest
        with st.expander(f"Q: {item['question'][:80]}{'…' if len(item['question']) > 80 else ''}", expanded=False):
            st.markdown(str(item["report"]))
            st.markdown(f"""
            <div class="scores-wrap">
                <div class="scores-title">Quality Scores</div>
                <div class="score-row">
                    <div class="score-name">Faithfulness</div>
                    <div class="score-track"><div class="score-fill" style="width:{item['faith']*100:.0f}%;background:{bar_color(item['faith'])};"></div></div>
                    <div class="score-num" style="color:{bar_color(item['faith'])}">{item['faith']:.2f}</div>
                </div>
                <div class="score-row">
                    <div class="score-name">Answer Relevancy</div>
                    <div class="score-track"><div class="score-fill" style="width:{item['rel']*100:.0f}%;background:{bar_color(item['rel'])};"></div></div>
                    <div class="score-num" style="color:{bar_color(item['rel'])}">{item['rel']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
# ── Result display ─────────────────────────────────────────────────────────────
if st.session_state.report:
    f = st.session_state.faith_score
    r = st.session_state.rel_score

    # Answer panel
    st.markdown("""
    <div class="result-wrap">
        <div class="result-head">
            <span class="result-head-dot"></span>
            <span class="result-head-label">Verified Answer</span>
        </div>
        <div class="result-body">
    """, unsafe_allow_html=True)

    report_text = st.session_state.report
    if hasattr(report_text, 'raw'):
        report_text = report_text.raw
    st.markdown(str(report_text))

    st.markdown('</div></div>', unsafe_allow_html=True)

    # Score bars
    st.markdown(f"""
    <div class="scores-wrap">
        <div class="scores-title">Quality Scores</div>
        <div class="score-row">
            <div class="score-name">Faithfulness</div>
            <div class="score-track">
                <div class="score-fill" style="width:{f*100:.0f}%;background:{bar_color(f)};"></div>
            </div>
            <div class="score-num" style="color:{bar_color(f)}">{f:.2f}</div>
        </div>
        <div class="score-row">
            <div class="score-name">Answer Relevancy</div>
            <div class="score-track">
                <div class="score-fill" style="width:{r*100:.0f}%;background:{bar_color(r)};"></div>
            </div>
            <div class="score-num" style="color:{bar_color(r)}">{r:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status message
    if f >= 0.75 and r >= 0.75:
        st.success("High-confidence answer — both faithfulness and relevancy passed.")
    elif f < 0.5:
        st.error("Faithfulness is low — the answer may not be grounded in your documents. Try ingesting a relevant source.")
    elif r < 0.5:
        st.warning("Relevancy is low — the answer may have drifted from your question. Try rephrasing.")
    else:
        st.info("Scores are moderate. Ingesting a more targeted document will improve faithfulness.")
