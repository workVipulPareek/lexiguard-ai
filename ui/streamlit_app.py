import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="LexiGuard AI",
    page_icon="⚖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Global Styles ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    [data-testid="stAppViewContainer"] {
        padding: 2rem 1rem;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Card */
    .card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }

    /* Label above card */
    .card-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.4rem;
    }

    /* Answer text */
    .answer-text {
        font-size: 1.05rem;
        line-height: 1.75;
        color: #e2e8f0;
    }

    /* Risk badge */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-high   { background-color: #ef444422; color: #ef4444; border: 1px solid #ef4444; }
    .badge-medium { background-color: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b; }
    .badge-low    { background-color: #10b98122; color: #10b981; border: 1px solid #10b981; }

    /* Risk reasoning text */
    .risk-reasoning {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.6rem;
        line-height: 1.6;
    }

    /* Clause tags */
    .tag-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.3rem; }
    .tag {
        background-color: #0f172a;
        border: 1px solid #475569;
        color: #94a3b8;
        border-radius: 6px;
        padding: 0.2rem 0.65rem;
        font-size: 0.78rem;
        font-family: monospace;
    }

    /* Compliance items */
    .compliance-item {
        font-size: 0.88rem;
        padding: 0.25rem 0;
        color: #cbd5e1;
    }
    .dot-pass { color: #10b981; margin-right: 0.4rem; }
    .dot-fail { color: #ef4444; margin-right: 0.4rem; }

    /* Source excerpt */
    .source-text {
        font-size: 0.82rem;
        color: #64748b;
        background: #0f172a;
        border-left: 3px solid #334155;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-family: monospace;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Divider */
    hr { border-color: #1e293b; }

    /* Input overrides */
    [data-testid="stTextInput"] input {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border: 1px dashed #334155 !important;
        border-radius: 8px !important;
    }

    /* Button */
    [data-testid="stButton"] > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: background 0.2s;
    }
    [data-testid="stButton"] > button:hover {
        background-color: #2563eb;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #64748b !important;
        font-size: 0.82rem !important;
    }

    /* History item */
    .history-item {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .history-q {
        color: #e2e8f0;
        font-weight: 500;
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Helper Renderers ────────────────────────────────────────────

def render_risk_badge(level: str) -> str:
    cls = f"badge-{level.lower()}"
    return f'<span class="badge {cls}">{level.upper()}</span>'


def render_tags(items: list) -> str:
    tags = "".join(f'<span class="tag">{i.replace("_", " ")}</span>' for i in items)
    return f'<div class="tag-row">{tags}</div>'


def render_result(data: dict):
    answer = data.get("answer", "")
    risk   = data.get("risk_score", "unknown").lower()
    clauses = data.get("clause_types", [])
    passed  = data.get("compliance_passed", [])
    failed  = data.get("compliance_failed", [])
    chunks  = data.get("source_chunks", [])

    # Parse answer block into components
    direct_answer = ""
    reasoning     = ""
    source_text   = chunks[0][:400] if chunks else ""

    lines = answer.splitlines()
    section = None
    buf = []
    for line in lines:
        stripped = line.strip()
        if stripped == "DIRECT ANSWER":
            section = "answer"; buf = []
        elif stripped == "RISK ASSESSMENT":
            if section == "answer":
                direct_answer = "\n".join(buf).strip()
            section = "risk"; buf = []
        elif stripped == "SOURCE EXCERPT":
            section = "source"; buf = []
        elif stripped.startswith("Reasoning:") and section == "risk":
            reasoning = stripped.replace("Reasoning:", "").strip()
        elif section == "answer":
            buf.append(line)

    if section == "answer" and not direct_answer:
        direct_answer = "\n".join(buf).strip()

    if not direct_answer:
        direct_answer = answer[:600]

    # ── Answer Card ──
    st.markdown('<div class="card-label">Answer</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card"><div class="answer-text">{direct_answer}</div></div>',
        unsafe_allow_html=True
    )

    # ── Risk + Clauses (side by side) ──
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card-label">Risk Level</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card">{render_risk_badge(risk)}</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown('<div class="card-label">Identified Clauses</div>', unsafe_allow_html=True)
        tag_html = render_tags(clauses) if clauses else '<span style="color:#475569">None identified</span>'
        st.markdown(
            f'<div class="card">{tag_html}</div>',
            unsafe_allow_html=True
        )

    # ── Compliance ──
    st.markdown('<div class="card-label">Compliance Check</div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            passed_html = "".join(
                f'<div class="compliance-item"><span class="dot-pass">✔</span>{p}</div>'
                for p in passed
            ) or '<div class="compliance-item" style="color:#475569">None</div>'
            st.markdown(
                f'<div class="card"><div style="font-size:0.72rem;color:#10b981;'
                f'letter-spacing:0.08em;margin-bottom:0.5rem">PASSED</div>{passed_html}</div>',
                unsafe_allow_html=True
            )
        with c2:
            failed_html = "".join(
                f'<div class="compliance-item"><span class="dot-fail">✘</span>{f}</div>'
                for f in failed
            ) or '<div class="compliance-item" style="color:#475569">None</div>'
            st.markdown(
                f'<div class="card"><div style="font-size:0.72rem;color:#ef4444;'
                f'letter-spacing:0.08em;margin-bottom:0.5rem">FAILED</div>{failed_html}</div>',
                unsafe_allow_html=True
            )

    # ── Expandable: Reasoning ──
    if reasoning:
        with st.expander("Risk Reasoning"):
            st.markdown(
                f'<div class="risk-reasoning">{reasoning}</div>',
                unsafe_allow_html=True
            )

    # ── Expandable: Source Excerpt ──
    if source_text:
        with st.expander("Source Excerpt"):
            st.markdown(
                f'<div class="source-text">{source_text}</div>',
                unsafe_allow_html=True
            )


# ── Header ─────────────────────────────────────────────────────

st.markdown("""
<div style="margin-bottom:2rem">
    <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0;letter-spacing:-0.02em">
        ⚖ LexiGuard AI
    </div>
    <div style="font-size:0.85rem;color:#64748b;margin-top:0.2rem">
        Smart Contract Analyzer
    </div>
</div>
""", unsafe_allow_html=True)


# ── Upload ──────────────────────────────────────────────────────

st.markdown('<div class="card-label">Contract File</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="upload",
    type=["txt", "pdf"],
    label_visibility="collapsed"
)

if uploaded_file:
    if st.session_state.get("last_uploaded") != uploaded_file.name:
        with st.spinner("Uploading..."):
            response = requests.post(
                f"{API_BASE}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "text/plain")}
            )
        if response.status_code == 200:
            saved_name = response.json().get("filename", uploaded_file.name)
            st.session_state["filename"] = saved_name
            st.session_state["last_uploaded"] = uploaded_file.name
            st.success(f"Ready — {uploaded_file.name}")
        else:
            st.error(f"Upload failed: {response.text}")
    else:
        st.success(f"Ready — {uploaded_file.name}")


# ── Query ───────────────────────────────────────────────────────

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="card-label">Question</div>', unsafe_allow_html=True)
question = st.text_input(
    label="question",
    placeholder="e.g. What are the payment penalties?",
    label_visibility="collapsed"
)

analyze = st.button("Analyze Contract")

if analyze:
    if not question.strip():
        st.warning("Please enter a question.")
    elif "filename" not in st.session_state:
        st.warning("Please upload a contract file first.")
    else:
        with st.spinner("Analyzing..."):
            response = requests.post(
                f"{API_BASE}/query",
                json={
                    "question": question,
                    "filename": st.session_state["filename"]
                }
            )

        if response.status_code == 200:
            data = response.json()

            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].append({
                "question": question,
                "data": data
            })

            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#64748b;margin-bottom:1rem">Analysis Result</div>',
                unsafe_allow_html=True
            )
            render_result(data)

        else:
            st.error(f"Query failed: {response.text}")


# ── History ─────────────────────────────────────────────────────

if st.session_state.get("history"):
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
        'text-transform:uppercase;color:#64748b;margin-bottom:0.75rem">Recent Queries</div>',
        unsafe_allow_html=True
    )

    for entry in reversed(st.session_state["history"][-5:]):
        risk = entry["data"].get("risk_score", "").lower()
        badge = render_risk_badge(risk) if risk else ""
        clauses = entry["data"].get("clause_types", [])
        clause_str = ", ".join(clauses[:4]) if clauses else "—"
        st.markdown(f"""
        <div class="history-item">
            <div class="history-q">{entry['question']}</div>
            <div style="display:flex;align-items:center;gap:0.75rem;margin-top:0.3rem">
                {badge}
                <span style="font-size:0.78rem;color:#475569">{clause_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Clear History", key="clear"):
        st.session_state["history"] = []
        st.rerun()