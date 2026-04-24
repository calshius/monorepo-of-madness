"""Web search and photosynthesis data tools for the benchmark agent.

Uses the DuckDuckGo Instant Answer API — free, no API key required.
"""

import requests
from langchain_core.tools import tool

_tool_call_count = 0

_DDG_URL = "https://api.duckduckgo.com/"


def reset_tool_call_count() -> None:
    global _tool_call_count
    _tool_call_count = 0


def get_tool_call_count() -> int:
    return _tool_call_count


@tool
def search_knowledge_base(query: str) -> str:
    """Search the web for information about a topic.

    Args:
        query: The topic to look up.

    Returns:
        A plain-text summary of the topic from the web.
    """
    global _tool_call_count
    _tool_call_count += 1

    resp = requests.get(
        _DDG_URL,
        params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    abstract_text = data.get("AbstractText", "").strip()
    if abstract_text:
        source = data.get("AbstractSource", "")
        return f"{abstract_text} (Source: {source})" if source else abstract_text

    # Fall back to top related topics
    topics = data.get("RelatedTopics", [])
    snippets = [
        t["Text"]
        for t in topics[:3]
        if isinstance(t, dict) and "Text" in t
    ]
    if snippets:
        return " ".join(snippets)

    return f"No web results found for '{query}'."


@tool
def photosynthesis_data_collector(flower_type: str) -> str:
    """Collect specific data about photosynthesis in different flower types.

    Args:
        flower_type: Type of flower to get photosynthesis data for (e.g., 'rose', 'sunflower', 'orchid')

    Returns:
        Photosynthesis-specific information about the flower type.
    """
    global _tool_call_count
    _tool_call_count += 1
    
    # Simulate specialized photosynthesis data collection
    flower_data = {
        "rose": "Roses perform C3 photosynthesis with optimal rates at 25°C. Their stomatal density varies by cultivar affecting CO2 uptake efficiency.",
        "sunflower": "Sunflowers exhibit high photosynthetic rates due to large leaf area and heliotropic movement maximizing light capture. C3 pathway with Rubisco activity peaking midday.",
        "orchid": "Orchids often use CAM photosynthesis in arid adaptations, opening stomata at night to reduce water loss while fixing CO2.",
        "tomato": "Tomato plants show inducible C4-like photosynthesis under high light stress, with bundle sheath chloroplasts enhancing CO2 concentration.",
        "maize": "Maize is a classic C4 plant with Kranz anatomy, showing 50% higher photosynthetic efficiency than C3 plants under high temperature and light.",
        "default": f"General photosynthesis data for {flower_type}: Involves light-dependent reactions producing ATP/NADPH, followed by Calvin cycle fixing CO2 into carbohydrates. Occurs in chloroplasts with chlorophyll absorbing light energy."
    }
    
    return flower_data.get(flower_type.lower(), flower_data["default"])