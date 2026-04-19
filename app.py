import json
import os
import re
from io import BytesIO
from typing import Any, Optional

import streamlit as st
from docx import Document
from pypdf import PdfReader

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import anthropic
except Exception:
    anthropic = None

st.set_page_config(
    page_title="Document Insight",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f6f8fb;
    --surface: #ffffff;
    --surface-2: #fbfcfe;
    --border: #e7ebf3;
    --text: #0f172a;
    --muted: #5b6474;
    --accent: #2563eb;
    --accent-soft: #eff6ff;
    --success: #166534;
    --success-soft: #ecfdf3;
    --warning: #b45309;
    --warning-soft: #fff7ed;
    --danger: #b91c1c;
    --danger-soft: #fef2f2;
    --shadow: 0 12px 34px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"]  {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.05), transparent 24%),
        linear-gradient(180deg, #fbfcff 0%, var(--bg) 100%);
    color: var(--text);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    color: #111827 !important;
}

.app-shell {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.app-header {
    background: rgba(255,255,255,0.88);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.4rem 1.5rem;
    box-shadow: var(--shadow);
}

.app-header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.app-title {
    font-size: 2rem;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
}

.app-subtitle {
    margin-top: 0.45rem;
    max-width: 780px;
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.55;
}

.header-chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.95rem;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 0.72rem;
    border-radius: 999px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.84rem;
    font-weight: 600;
}

.workspace-grid {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 1.25rem;
    align-items: stretch;
    margin-top: 0.25rem;
    margin-bottom: 1rem;
}

.surface {
    background: rgba(255,255,255,0.9);
    border: 1px solid var(--border);
    border-radius: 22px;
    box-shadow: var(--shadow);
    padding: 1.18rem;
}

.surface-tight {
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--border);
    border-radius: 20px;
    box-shadow: var(--shadow);
    padding: 1.18rem;
    height: 100%;
}

.section-label {
    color: #334155;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-bottom: 0.32rem;
}

.section-title {
    color: var(--text);
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.section-copy {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.55;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin-top: 0.4rem;
    margin-bottom: 0.2rem;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem;
    min-height: 112px;
}

.metric-label {
    color: var(--muted);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.metric-value {
    color: var(--text);
    font-size: 1.55rem;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.02em;
    word-break: break-word;
}

.metric-subtext {
    color: var(--muted);
    margin-top: 0.4rem;
    font-size: 0.82rem;
}

.flag-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 0.8rem 0.9rem;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--surface-2);
    margin-bottom: 0.65rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.32rem 0.62rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid transparent;
}

.badge-neutral {
    color: var(--muted);
    background: #f8fafc;
    border-color: var(--border);
}

.badge-high {
    color: var(--danger);
    background: var(--danger-soft);
}

.badge-medium {
    color: var(--warning);
    background: var(--warning-soft);
}

.badge-low {
    color: var(--success);
    background: var(--success-soft);
}

.kv-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.8rem;
}

.kv-card {
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--surface-2);
    padding: 0.85rem 0.9rem;
}

.kv-label {
    color: var(--muted);
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.kv-value {
    color: var(--text);
    font-size: 1rem;
    font-weight: 700;
}

.list-clean {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--text);
}

.list-clean li {
    margin-bottom: 0.45rem;
    line-height: 1.5;
}

.tag-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.upload-caption {
    color: #475569;
    font-size: 0.9rem;
    margin-top: 0.35rem;
}

.upload-panel {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
}

div[data-testid="stFileUploader"] {
    border: 1px dashed #94a3b8;
    border-radius: 18px;
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    padding: 0.95rem;
    margin-top: 0.15rem;
}

div[data-testid="stFileUploader"] section {
    padding: 0.2rem;
}

div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
    color: #334155 !important;
}

div[data-testid="stFileUploader"] button {
    min-height: 3rem;
    padding: 0.75rem 1rem;
    border-radius: 14px;
    border: 1px solid #bfdbfe !important;
    background: #eff6ff !important;
    color: #0f172a !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploader"] button *,
div[data-testid="stFileUploader"] button span {
    color: #0f172a !important;
    fill: #0f172a !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploader"] button:hover {
    background: #dbeafe !important;
    border-color: #93c5fd !important;
}

div[data-testid="stFileUploader"] button svg {
    fill: #1d4ed8 !important;
    color: #1d4ed8 !important;
}

label[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p {
    color: #334155;
}

.stTextInput label p,
.stTextArea label p,
.stSelectbox label p,
.stRadio label p,
.stFileUploader label p,
div[data-testid="stFileUploader"] label p {
    color: #334155 !important;
    font-weight: 700 !important;
}

@media (prefers-color-scheme: dark) {
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.10), transparent 26%),
            linear-gradient(180deg, #0b1220 0%, #0f172a 100%);
        color: #e5eefb;
    }

    .app-header,
    .surface,
    .surface-tight {
        background: rgba(15, 23, 42, 0.88);
        border-color: rgba(148, 163, 184, 0.20);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.35);
    }

    .app-title,
    .section-title,
    .metric-value,
    .kv-value,
    .list-clean,
    .list-clean li {
        color: #f8fafc !important;
    }

    .app-subtitle,
    .chip,
    .metric-label,
    .metric-subtext,
    .kv-label,
    .section-copy,
    .upload-caption,
    .section-label,
    label[data-testid="stWidgetLabel"] p,
    .stTextInput label p,
    .stTextArea label p,
    .stSelectbox label p,
    .stRadio label p,
    .stFileUploader label p,
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] *,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileData"] {
        color: #dbe7f5 !important;
    }

    .chip,
    .metric-card,
    .flag-row,
    .kv-card,
    .badge-neutral,
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.72) !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
    }

    div[data-testid="stFileUploader"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(17, 24, 39, 0.92) 100%);
        border: 1px dashed rgba(96, 165, 250, 0.6);
    }

    div[data-testid="stFileUploader"] button {
        background: linear-gradient(180deg, #dbeafe 0%, #bfdbfe 100%) !important;
        border-color: #93c5fd !important;
        color: #0f172a !important;
    }

    div[data-testid="stFileUploader"] button *,
    div[data-testid="stFileUploader"] button span,
    div[data-testid="stFileUploader"] button svg {
        color: #0f172a !important;
        fill: #0f172a !important;
        opacity: 1 !important;
    }

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.80) !important;
        color: #f8fafc !important;
        border-color: rgba(148, 163, 184, 0.25) !important;
    }
}

.stButton > button, .stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid transparent;
    background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    font-weight: 700;
    padding: 0.62rem 1rem;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.2);
}

.stTextArea textarea, .stTextInput input {
    border-radius: 14px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 0.45rem 0.85rem;
    background: rgba(255,255,255,0.76);
    border: 1px solid var(--border);
    height: auto;
}

.stTabs [aria-selected="true"] {
    background: #eef4ff !important;
    border-color: #bfdbfe !important;
}

hr {
    border-color: var(--border);
}

@media (max-width: 1100px) {
    .workspace-grid, .metric-grid, .kv-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def extract_text(uploaded_file) -> str:
    suffix = uploaded_file.name.lower().split(".")[-1]
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    if suffix == "pdf":
        reader = PdfReader(BytesIO(raw))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n\n".join(pages).strip()

    if suffix == "docx":
        doc = Document(BytesIO(raw))
        return "\n".join([p.text for p in doc.paragraphs]).strip()

    if suffix in {"txt", "md", "csv", "json"}:
        return raw.decode("utf-8", errors="ignore").strip()

    raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, MD, CSV, or JSON.")


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def estimate_doc_type(text: str, filename: str) -> str:
    lower = (filename + "\n" + text[:2500]).lower()
    mapping = {
        "Invoice": ["invoice", "vat", "subtotal", "amount due"],
        "Contract": ["agreement", "party", "term", "termination", "liability"],
        "Policy": ["policy", "purpose", "scope", "responsibilities"],
        "Report": ["report", "findings", "summary", "recommendation"],
        "Medical / Sensitive": ["nhs", "patient", "dob", "treatment", "medical"],
    }
    scores = {doc_type: sum(1 for term in terms if term in lower) for doc_type, terms in mapping.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General Document"


def detect_flags(text: str) -> dict[str, Any]:
    flags = {
        "Email addresses": len(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)),
        "Phone numbers": len(re.findall(r"(?:\+?44|0)\s?\d(?:[\d\s()-]{7,}\d)", text)),
        "National Insurance-like": len(re.findall(r"\b[A-CEGHJ-PR-TW-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b", text, re.I)),
        "Dates of birth-like": len(re.findall(r"\b(?:0?[1-9]|[12]\d|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:19|20)\d\d\b", text)),
        "Postcodes": len(re.findall(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", text, re.I)),
        "Bank / IBAN-like": len(re.findall(r"\b(?:IBAN|sort code|account number)\b", text, re.I)),
    }
    total = sum(flags.values())
    if total >= 8:
        level = "High"
    elif total >= 3:
        level = "Medium"
    else:
        level = "Low"
    return {"flags": flags, "risk": level, "total": total}


def truncate_text(text: str, max_chars: int = 18000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Truncated for analysis due to model input limit.]"


def build_prompt(text: str, filename: str, detected_type: str):
    return f"""
You are an expert document intelligence assistant used in a professional records and information management environment.

Analyse the uploaded document and return STRICT JSON with this exact structure:
{{
  "summary": "2-4 sentence executive summary",
  "document_type": "best guess at document type",
  "key_points": ["point 1", "point 2", "point 3"],
  "entities": [
    {{"type": "Person|Organisation|Location|Date|Reference|Other", "value": "..."}}
  ],
  "risk_flags": [
    {{"level": "High|Medium|Low", "issue": "...", "reason": "..."}}
  ],
  "recommended_actions": ["action 1", "action 2"],
  "search_tags": ["tag1", "tag2", "tag3"]
}}

Rules:
- Be practical, concise, and operationally useful.
- Prioritise document triage, records handling, confidentiality, review status, and indexing value.
- Highlight missing metadata, retention, redaction, classification, or escalation concerns where relevant.
- Only return valid JSON.

Filename: {filename}
Detected type: {detected_type}

Document content:
{text}
""".strip()


def analyse_with_openai(api_key: str, model: str, prompt: str) -> dict:
    if OpenAI is None:
        raise RuntimeError("The openai package is not installed.")
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=0.2,
    )
    content = getattr(response, "output_text", None)
    if not content:
        raise RuntimeError("No response text returned by OpenAI.")
    return json.loads(content)


def analyse_with_anthropic(api_key: str, model: str, prompt: str) -> dict:
    if anthropic is None:
        raise RuntimeError("The anthropic package is not installed.")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1400,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    chunks = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)
    content = "".join(chunks)
    return json.loads(content)


def render_badge(text: str, level: Optional[str] = None) -> str:
    css = "badge-neutral"
    if level:
        css = f"badge-{level.lower()}"
    return f'<span class="badge {css}">{text}</span>'


def html_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def normalise_result(result: Optional[dict], detected_type: str) -> dict:
    if not result:
        return {
            "summary": "AI analysis has not been run yet.",
            "document_type": detected_type,
            "key_points": [],
            "entities": [],
            "risk_flags": [],
            "recommended_actions": [],
            "search_tags": [],
        }
    return {
        "summary": result.get("summary", "No summary returned."),
        "document_type": result.get("document_type", detected_type),
        "key_points": result.get("key_points", []) or [],
        "entities": result.get("entities", []) or [],
        "risk_flags": result.get("risk_flags", []) or [],
        "recommended_actions": result.get("recommended_actions", []) or [],
        "search_tags": result.get("search_tags", []) or [],
    }


with st.sidebar:
    st.markdown("## Document Insight")
    st.caption("Configuration")

    provider = st.selectbox("AI provider", ["Anthropic", "OpenAI"])
    if provider == "Anthropic":
        default_model = "claude-3-5-sonnet-latest"
        api_key = st.text_input(
            "Anthropic API key",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password",
            placeholder="Enter API key",
        )
    else:
        default_model = "gpt-4.1-mini"
        api_key = st.text_input(
            "OpenAI API key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            placeholder="Enter API key",
        )

    model = st.text_input("Model", value=default_model)
    analysis_mode = st.radio("Analysis mode", ["AI + heuristics", "Heuristics only"], index=0)

    st.markdown("---")
    st.caption("Supported formats")
    st.write("PDF, DOCX, TXT, MD, CSV, JSON")
    st.caption("Outputs")
    st.write("Summary, document type, entities, risk flags, actions, and tags")


st.markdown(
    """
    <div class="app-shell">
        <div class="app-header">
            <div class="app-header-row">
                <div>
                    <div class="app-title">Document Insight</div>
                    <div class="app-subtitle">
                        Analyse business documents, surface sensitivity indicators, generate structured summaries,
                        and prepare records for faster triage and review.
                    </div>
                    <div class="header-chip-row">
                        <span class="chip">Document triage</span>
                        <span class="chip">Structured AI analysis</span>
                        <span class="chip">Sensitivity review</span>
                        <span class="chip">Search-ready metadata</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="workspace-grid">', unsafe_allow_html=True)
left_panel, right_panel = st.columns([1.12, 0.88], gap="large")

with left_panel:
    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="surface">
            <div class="section-label">Input</div>
            <div class="section-title">Upload document</div>
            <div class="section-copy">Select a file to extract content and generate a structured review.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt", "md", "csv", "json"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="upload-caption">Supported formats: PDF, DOCX, TXT, MD, CSV, JSON</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_panel:
    st.markdown(
        """
        <div class="surface-tight">
            <div class="section-label">Review mode</div>
            <div class="section-title">Analysis workflow</div>
            <div class="section-copy">
                The workspace combines extraction, heuristic sensitivity checks, and optional AI analysis to support
                document handling, indexing, and initial review.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

if not uploaded:
    st.markdown(
        """
        <div class="surface" style="margin-top:1rem;">
            <div class="section-label">Ready</div>
            <div class="section-title">No document loaded</div>
            <div class="section-copy">Upload a document to begin analysis.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

try:
    text = extract_text(uploaded)
    if not text.strip():
        st.warning("No extractable text was found in the uploaded file.")
        st.stop()
except Exception as exc:
    st.error(f"Unable to process file: {exc}")
    st.stop()

heuristic = detect_flags(text)
detected_type = estimate_doc_type(text, uploaded.name)
words = count_words(text)
chars = len(text)
file_ext = uploaded.name.split(".")[-1].upper()

analysis_result: Optional[dict] = None
prompt = build_prompt(truncate_text(text), uploaded.name, detected_type)

if analysis_mode == "AI + heuristics" and api_key:
    with st.spinner("Running analysis..."):
        try:
            if provider == "Anthropic":
                analysis_result = analyse_with_anthropic(api_key, model, prompt)
            else:
                analysis_result = analyse_with_openai(api_key, model, prompt)
        except Exception as exc:
            st.error(f"AI analysis failed: {exc}")
elif analysis_mode == "AI + heuristics" and not api_key:
    st.info("Add an API key in the sidebar to enable AI analysis. Heuristic review is still available.")

result = normalise_result(analysis_result, detected_type)
risk_level = heuristic["risk"]

metric_html = f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-label">Filename</div>
        <div class="metric-value" style="font-size:1.08rem;">{html_escape(uploaded.name)}</div>
        <div class="metric-subtext">{file_ext} document</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Document type</div>
        <div class="metric-value" style="font-size:1.2rem;">{html_escape(result['document_type'])}</div>
        <div class="metric-subtext">Estimated from content</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Word count</div>
        <div class="metric-value">{words:,}</div>
        <div class="metric-subtext">{chars:,} characters extracted</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Sensitivity risk</div>
        <div class="metric-value">{html_escape(risk_level)}</div>
        <div class="metric-subtext">{heuristic['total']} indicators detected</div>
    </div>
</div>
"""
st.markdown(metric_html, unsafe_allow_html=True)

main_tab, text_tab, json_tab = st.tabs(["Analysis", "Extracted Text", "Structured Output"])

with main_tab:
    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Executive review</div>', unsafe_allow_html=True)
        st.write(result["summary"])

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="kv-grid">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="kv-card">
                <div class="kv-label">Review status</div>
                <div class="kv-value">Needs validation</div>
            </div>
            <div class="kv-card">
                <div class="kv-label">Suggested owner</div>
                <div class="kv-value">Information Governance / Operations</div>
            </div>
            <div class="kv-card">
                <div class="kv-label">Indexing status</div>
                <div class="kv-value">Ready after review</div>
            </div>
            <div class="kv-card">
                <div class="kv-label">Risk level</div>
                <div class="kv-value">{html_escape(risk_level)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.85rem'></div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown("**Key points**")
            if result["key_points"]:
                st.markdown(
                    "<ul class='list-clean'>" + "".join(f"<li>{html_escape(item)}</li>" for item in result["key_points"][:8]) + "</ul>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No key points available.")
        with col_b:
            st.markdown("**Recommended actions**")
            if result["recommended_actions"]:
                st.markdown(
                    "<ul class='list-clean'>" + "".join(f"<li>{html_escape(item)}</li>" for item in result["recommended_actions"][:8]) + "</ul>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No recommended actions available.")

        st.markdown("<div style='height:0.85rem'></div>", unsafe_allow_html=True)
        st.markdown("**Search tags**")
        if result["search_tags"]:
            st.markdown(
                f"<div class='tag-wrap'>{''.join(render_badge(html_escape(tag)) for tag in result['search_tags'][:12])}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("No search tags available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Sensitivity review</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Heuristic indicators</div>', unsafe_allow_html=True)
        st.markdown(render_badge(f"Risk: {risk_level}", risk_level), unsafe_allow_html=True)
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        for label, value in heuristic["flags"].items():
            st.markdown(
                f"<div class='flag-row'><div>{html_escape(label)}</div><div>{render_badge(str(value))}</div></div>",
                unsafe_allow_html=True,
            )

        if result["risk_flags"]:
            st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
            st.markdown("**AI risk flags**")
            for flag in result["risk_flags"][:6]:
                level = str(flag.get("level", "Low")).title()
                issue = flag.get("issue", "Issue")
                reason = flag.get("reason", "")
                st.markdown(render_badge(level, level), unsafe_allow_html=True)
                st.write(f"**{issue}** — {reason}")

        if result["entities"]:
            st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
            st.markdown("**Detected entities**")
            for entity in result["entities"][:12]:
                st.write(f"**{entity.get('type', 'Other')}** — {entity.get('value', '')}")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.download_button(
            "Download analysis JSON",
            data=json.dumps(result, indent=2),
            file_name=f"{os.path.splitext(uploaded.name)[0]}-analysis.json",
            mime="application/json",
        )
        st.markdown('</div>', unsafe_allow_html=True)

with text_tab:
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Content</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Extracted text</div>', unsafe_allow_html=True)
    st.text_area("Extracted text", value=text[:25000], height=560, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with json_tab:
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Output</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Structured analysis</div>', unsafe_allow_html=True)
    st.code(json.dumps(result, indent=2), language="json")
    st.markdown('</div>', unsafe_allow_html=True)
