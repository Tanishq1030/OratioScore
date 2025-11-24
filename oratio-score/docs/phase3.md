# Phase 3 — Frontend Integration (Streamlit ↔ FastAPI)

## Overview
Phase 3 connects the scoring backend to the Streamlit frontend to provide an interactive user interface for score computation.

---

## Objectives
- Call `/score` from Streamlit.
- Display all scoring components and feedback.
- Provide a clean, visual UI for reviewers.
- Add error-handling and UX improvements.

---

## Deliverables

### 1. Backend Integration
Streamlit calls:
```python
requests.post(BACKEND_URL + "/score", json={"text": transcript})
```

### 2. Frontend Layout Improvements
- Big text area for transcript input.
- Upload support for .txt files.
- Button to trigger scoring.
- Summary card with overall score.
- Table of per-criterion scores.
- Expanders for matched keywords, semantics, penalties.
- LLM feedback formatted neatly.

### 3. Error Handling
- No input → warning.
- Backend down → error toast.
- Malformed response → fallback to raw JSON.

### 4. Config
`st.secrets["BACKEND_URL"]` added to support deployment.

## Phase Completion Criteria
- Frontend now fully operational.
- User can paste transcript → get detailed scores.
- Layout is professional and readable.
