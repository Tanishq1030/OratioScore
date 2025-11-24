# Architecture Diagram

```mermaid
flowchart TD

Frontend[Streamlit Frontend<br>Transcript Input] -->|POST /score| Backend[FastAPI Backend]

Backend --> NLP[NLP Utils<br>Clean + Tokenize + Keywords]
Backend --> Embed[Sentence Transformers<br>Semantic Embeddings]
Backend --> ScoreEngine[Scoring Engine<br>Keyword + Semantic + Length + Weight]
Backend --> Rubric[Rubric Loader (Excel)]
Backend --> LLM[LangChain Feedback Layer]

ScoreEngine --> FinalScore[Overall Score 0–100]
LLM --> Feedback[Criterion-level Feedback]

Frontend <--|JSON Response| Backend
```
