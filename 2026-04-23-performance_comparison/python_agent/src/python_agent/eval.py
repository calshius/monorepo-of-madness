"""LLM-as-judge evaluation for the photosynthesis benchmark."""

import json
import re

from langchain_core.messages import HumanMessage

_EVAL_PROMPT = """\
You are an expert biology teacher evaluating an answer comparing photosynthesis in different flower types.

Key concepts that a complete, accurate answer should cover:
1. Basic photosynthesis process: Light energy conversion to chemical energy (glucose / ATP)
2. Reactants and products: CO2 and H2O as inputs, glucose (C6H12O6) and O2 as outputs
3. Cellular location: chloroplasts (thylakoid membranes and stroma) where photosynthesis occurs
4. Two-stage process: light-dependent reactions and Calvin cycle (light-independent reactions)
5. Photosynthetic pathways: Differences between C3, C4, and CAM mechanisms
6. Environmental adaptations: How different flowers adapt photosynthesis to their environments (light, water, temperature)
7. Structural variations: Leaf anatomy differences affecting photosynthetic efficiency between species
8. Comparative analysis: Specific differences between rose and sunflower photosynthesis capabilities

Answer to evaluate:
{answer}

Score the answer on two dimensions from 0 to 5:
- accuracy: Is the information factually correct? (0=completely wrong, 5=fully accurate)
- completeness: How well does the answer cover the 8 key concepts above? (0=none, 5=exceptionally thorough coverage)

Respond ONLY with JSON on a single line, no markdown:
{{"accuracy": <int 0-5>, "completeness": <int 0-5>, "reasoning": "<one sentence>"}}"""


async def evaluate_answer_async(answer: str, llm) -> dict:
    """Score the answer asynchronously on accuracy (0-5) and completeness (0-5)."""
    prompt = _EVAL_PROMPT.format(answer=answer)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    content = response.content
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    match = re.search(r"\{.*?\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"accuracy": -1, "completeness": -1, "reasoning": "eval parse error"}

