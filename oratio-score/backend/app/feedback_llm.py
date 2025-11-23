import os
from typing import Dict, List
import json

try:
    from langchain import LLMChain, PromptTemplate
    from langchain.output_parsers import StructuredOutputParser, OutputFixingParser

    try:
        from langchain.llms import AzureOpenAI

        LLM_AVAILABLE = True
        LLM_TYPE = "azure"
    except ImportError:
        try:
            from langchain.llms import OpenAI

            LLM_AVAILABLE = True
            LLM_TYPE = "openai"
        except ImportError:
            LLM_AVAILABLE = False
            LLM_TYPE = None
except ImportError:
    LLM_AVAILABLE = False
    LLM_TYPE = None

from app.config import settings


def generate_feedback_simple(transcript: List[Dict]) -> Dict[str, Dict]:
    """
    Deterministic fallback feedback generator.
    """

    out = {}
    for e in transcript:
        name = e.get("name", "unknown")
        kfound = e.get("keywords_found", []) or []
        sscore = float(e.get("semantic_score", 0.0))
        raw = float(e.get("raw_score", 0.0))
        if len(kfound) == 0 and sscore < 60.0:
            eval_text = "Low relevance to this criterion."
            suggestion = "Mention this topic explicitly and give a short example."
        elif len(kfound) > 0 and sscore >= 60.0:
            eval_text = "Good coverage of this criterion."
            suggestion = "Add a specific example to strengthen it."
        else:
            eval_text = "Partial coverage."
            suggestion = "Expand the relevant points and include keywords."
        justification = f"Keywords found: {kfound}. Semantic score: {sscore:.2f}. Computed raw score: {raw:.1f}."
        out[name] = {
            "evaluation": eval_text,
            "suggestion": suggestion,
            "justification": justification,
        }
    return out


def _build_prompt_and_parser():
    """
    Build prompt template and StructuredOutputParser that expects a JSON list of objects:
    [
    {"criterion":"...", "evaluation": "...", "suggestion": "...", "justification":"..."},
    ...
    ]
    """
    # We will instruct the LLM to output strict JSON for robust parsing
    template = """You are an objective assistant that writes short  (1-2 sentence) feedback message for student spoken-transcripts.
Given a list of criteria evidence evidence, produce a JSON array where each item has:
- criterion (string)
- evaluation (string, 1-2 sentences)
- suggestion (string, 1-2 sentences)
- justification (string, one sentence referencing keywords_found and semantic_score)

Input evidence:
{transcript_bolb}

Output (JSON array):"""
    prompt = PromptTemplate(input_variables=["transcript_bolb"], template=template)

    # We'll not rely on StructuredOutputParser for nested arrays here to keep the dependency simple;
    # Instead, we'll request JSON feedack an attempt to parse it.
    return prompt


def generate_feedback_llm(transcript: List[Dict]) -> Dict[str, Dict]:
    """
    Use LangChain to generate structured JSON feedback. If any step fails, fall back to deterministic generator.
    """
    if not LLM_AVAILABLE:
        return generate_feedback_simple(transcript)

    # Build transcript blob (string)
    transcript_bolb = json.dumps(transcript, indent=2)
    prompt = _build_prompt_and_parser()

    # init LLM
    try:
        if LLM_TYPE == "azure":
            llm = AzureOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                temperature=float(settings.LLM_TEMPERATURE),
            )
        else:
            llm = OpenAI(temperature=float(settings.LLM_TEMPERATURE))
        chain = LLMChain(llm=llm, prompt=prompt)
        raw_out = chain.run(transcript_bolb=transcript_bolb)
        # Expect raw_out to be JSON array
        parsed = json.loads(raw_out)
        # Convert to dictkeyed by criterion

        out = {}
        for item in parsed:
            crit = (
                item.get("criterion") or item.get("criterion_name") or item.get("name")
            )
            out[crit] = {
                "evaluation": item.get("evaluation", ""),
                "suggestion": item.get("suggestion", ""),
                "justification": item.get("justification", ""),
            }
        return out
    except Exception as e:
        # Fallback
        return generate_feedback_simple(transcript)
