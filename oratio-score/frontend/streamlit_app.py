# frontend/streamlit_app.py
import streamlit as st
import os
import requests

st.set_page_config(page_title="OratioScore - Demo", layout="centered")

st.title("OratioScore — Transcript Scoring (Phase 1)")
st.write(
    "Paste your transcript below and click **Score**. (Phase 1: skeleton scoring active)"
)

BACKEND_URL = os.environ.get("ORATIO_BACKEND_URL", "http://localhost:8000")

text = st.text_area("Transcript text", height=240)
uploaded = st.file_uploader("Or upload a .txt transcript", type=["txt"])
if uploaded is not None and not text:
    text = uploaded.read().decode("utf-8")

st.write("Word count:", len(text.split()) if text else 0)

if st.button("Score") and text:
    with st.spinner("Contacting backend..."):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/score", json={"text": text}, timeout=30
            )
            data = resp.json()
            st.json(data)
        except Exception as e:
            st.error(f"Request failed: {e}")
