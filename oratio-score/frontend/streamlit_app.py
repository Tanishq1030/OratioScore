# frontend/streamlit_app.py
import streamlit as st
import os
import requests
import time
from typing import Any, Dict, List
import json

# Ensure backend package is importable when Streamlit runs the frontend module
import sys

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
BACKEND_PATH = os.path.join(REPO_ROOT, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

from app.zon import zon_serialize

st.set_page_config(page_title="OratioScore - Demo", layout="wide")

st.header("OratioScore — Transcript Scoring")
st.markdown(
    "Paste a transcript or upload a .txt file, then click **Score** to evaluate."
)

# Backend configuration (can be set in Streamlit secrets)
# Resolve backend URL: prefer environment variable, then Streamlit secrets, then default.
try:
    BACKEND_URL = os.environ.get("ORATIO_BACKEND_URL") or st.secrets.get("BACKEND_URL")
except Exception:
    # If Streamlit secrets are not present (StreamlitSecretNotFoundError), fall back to env or default
    BACKEND_URL = os.environ.get("ORATIO_BACKEND_URL")

if not BACKEND_URL:
    BACKEND_URL = "http://localhost:8000"


def call_score_api(text: str, retries: int = 3, backoff: float = 0.5) -> Dict[str, Any]:
    url = f"{BACKEND_URL.rstrip('/')}/score"
    attempt = 0
    while True:
        try:
            resp = requests.post(url, json={"text": text}, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt >= retries:
                raise
            time.sleep(backoff * (2 ** (attempt - 1)))


def format_keywords(kws: List[str]) -> str:
    return ", ".join(kws) if kws else "—"


def score_color(score: float) -> str:
    """Return a hex color for a score 0..100 (green->yellow->red)."""
    try:
        s = max(0.0, min(100.0, float(score)))
    except Exception:
        return "#dddddd"
    # green (good) at 80+, yellow (mid) 50-80, red below 50
    if s >= 80:
        return "#16a34a"  # green-600
    if s >= 50:
        return "#f59e0b"  # amber-500
    return "#ef4444"  # red-500


col1, col2 = st.columns([3, 1])

with col1:
    # Use session state for the transcript so uploads populate and the user can edit the text
    if "transcript_text" not in st.session_state:
        st.session_state["transcript_text"] = ""

    uploaded = st.file_uploader("Or upload a .txt transcript", type=["txt"])
    if uploaded is not None:
        try:
            uploaded_text = uploaded.read().decode("utf-8")
            # always overwrite the session transcript with uploaded content so user can edit
            st.session_state["transcript_text"] = uploaded_text
        except Exception:
            st.error(
                "Failed to read uploaded file. Ensure it's a text file encoded in UTF-8."
            )

    text = st.text_area(
        "Transcript text",
        value=st.session_state.get("transcript_text", ""),
        height=320,
        key="transcript_text",
    )

    st.write("Word count:", len(text.split()) if text else 0)
    allow_score = bool(text and text.strip())
    if st.button("Score") and allow_score:
        with st.spinner("Contacting backend..."):
            try:
                data = call_score_api(text)
                st.session_state["last_result"] = data
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except json.JSONDecodeError:
                st.error("Backend returned invalid JSON.")

with col2:
    st.subheader("Settings")
    # Do not display the backend URL or environment hints in the UI.
    st.write("Backend: configured")


result = st.session_state.get("last_result")
if result:
    # Basic validation
    if not isinstance(result, dict):
        st.error("Unexpected response format from backend.")
    else:
        overall = result.get("overall_score")
        word_count = result.get("word_count")
        criteria = result.get("criteria", [])
        evidence = result.get("evidence", {})
        feedback = (
            result.get("feedback") or result.get("llm_feedback") or result.get("llm")
        )

        st.subheader("Results")
        top_cols = st.columns([1, 2, 2])
        with top_cols[0]:
            if overall is not None:
                st.metric("Overall Score", f"{overall:.2f}")
            else:
                st.write("Overall score not present")
        with top_cols[1]:
            st.write("**Word count**")
            st.write(word_count if word_count is not None else "—")
        with top_cols[2]:
            st.write("Weighted breakdown")
            try:
                names = [c.get("name") for c in criteria]
                values = [c.get("weighted_score", 0) for c in criteria]
                if names and values:
                    st.bar_chart({"weights": values}, x=names)
            except Exception:
                pass

        # Per-criterion scores (colored badges)
        st.markdown("**Per-criterion scores**")
        try:
            for c in criteria:
                name = c.get("name")
                raw = c.get("raw_score")
                weighted = c.get("weighted_score")
                kw_found = format_keywords(c.get("keywords_found", []))
                color = score_color(raw if raw is not None else weighted)
                cols = st.columns([3, 1, 1, 3])
                with cols[0]:
                    st.markdown(f"**{name}**")
                    st.caption(f"weight: {c.get('weight')}")
                with cols[1]:
                    st.markdown(
                        f"<div style='background:{color};color:#fff;padding:6px;border-radius:6px;text-align:center'>{(raw or 0):.1f}</div>",
                        unsafe_allow_html=True,
                    )
                with cols[2]:
                    st.markdown(f"{(weighted or 0):.2f}")
                with cols[3]:
                    expected_kws = format_keywords(c.get("keywords", []))
                    st.markdown(f"**Expected keywords:** {expected_kws}")
                    st.markdown(f"**Matched keywords:** {kw_found}")
            st.markdown("---")
        except Exception:
            st.write("Could not render per-criterion table")

        # Evidence and feedback
        with st.expander("Evidence (raw)", expanded=False):
            st.json(evidence)
            # ZON (default export)
            try:
                evidence_zon = zon_serialize(evidence)
            except Exception:
                evidence_zon = str(evidence)
            st.download_button(
                "Download Evidence (ZON) — default",
                evidence_zon,
                file_name="evidence.zon",
                mime="text/plain",
            )
            # JSON (secondary)
            try:
                evidence_json = json.dumps(evidence, indent=2)
            except Exception:
                evidence_json = str(evidence)
            st.download_button(
                "Download Evidence (JSON)",
                evidence_json,
                file_name="evidence.json",
                mime="application/json",
            )

        if feedback:
            with st.expander("LLM Feedback", expanded=True):
                # if feedback is dict with keys, pretty print
                if isinstance(feedback, dict):
                    for k, v in feedback.items():
                        st.markdown(f"**{k}**")
                        st.write(v)
                else:
                    st.write(feedback)

        # Full raw response
        with st.expander("Raw response JSON", expanded=False):
            st.json(result)
            # ZON (default)
            try:
                result_zon = zon_serialize(result)
            except Exception:
                result_zon = str(result)
            st.download_button(
                "Download Full Response (ZON) — default",
                result_zon,
                file_name="oratio_response.zon",
                mime="text/plain",
            )
            # JSON (secondary)
            try:
                result_json = json.dumps(result, indent=2)
            except Exception:
                result_json = str(result)
            st.download_button(
                "Download Full Response (JSON)",
                result_json,
                file_name="oratio_response.json",
                mime="application/json",
            )
