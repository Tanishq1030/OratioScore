# Phase 6 — Final Documentation & Demo

## Overview
Phase 6 prepares the deliverable package: final README, architecture diagram, scoring breakdown, and demo video.

---

## Deliverables

### 1. Final `README.md`
Includes:
- Project summary
- Architecture diagram
- Setup instructions
- Scoring explanation
- API docs
- Deployment links
- Demo video link

### 2. Architecture Diagram (Mermaid)
```
flowchart TD

A[Streamlit Frontend] -->|POST /score| B[FastAPI Backend]

B --> C[NLP Utils<br>- Cleaning<br>- Keywords<br>- Tokenization]

B --> D[Embeddings<br>Sentence Transformers]

B --> E[Scoring Engine<br>keyword + semantic + length + weight]

B --> F[Rubric Loader<br>Excel → Criteria]

B --> G[LLM Feedback Layer<br>LangChain]

E --> H[Overall Score 0–100]
G --> I[Per-Criterion Feedback]

A <--|JSON Response| B
```

### 3. Demo Video Script
- Open Streamlit.
- Paste transcript.
- Run score.
- Show:
  - overall score
  - criterion breakdown
  - keyword matches
  - semantic similarity
  - feedback
- State final output.

## Phase Completion Criteria
- Complete documentation bundle.
- Working demo video.
- Deployed app and GitHub repo ready for submission.
