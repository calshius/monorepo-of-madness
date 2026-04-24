"""LangGraph ReAct agent wired up for benchmarking."""

import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.agents import create_agent

from python_agent.tools import search_knowledge_base, photosynthesis_data_collector

BENCHMARK_PROMPT = (
    "Compare photosynthesis in roses and sunflowers. Use both the search_knowledge_base "
    "tool and the photosynthesis_data_collector tool to gather comprehensive information "
    "about the biochemical pathways, environmental adaptations, and efficiency differences."
)

_TOOLS = [search_knowledge_base, photosynthesis_data_collector]


def build_agent(model: str = "nvidia/nemotron-3-super-120b-a12b:free"):
    """Construct and return (compiled agent, llm) for benchmarking."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY environment variable is not set.")

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    return create_agent(llm, _TOOLS), llm


async def run_once_async(agent) -> tuple[str, int, dict]:
    """Run the agent asynchronously and return (final_answer, tool_calls_made, token_usage)."""
    result = await agent.ainvoke({"messages": [HumanMessage(content=BENCHMARK_PROMPT)]})

    # Count tool calls from ToolMessage instances (safe for concurrent runs)
    tool_calls = sum(1 for msg in result["messages"] if isinstance(msg, ToolMessage))

    # Accumulate token usage across all AI messages in the thread
    input_tokens = 0
    output_tokens = 0
    for msg in result["messages"]:
        usage = getattr(msg, "usage_metadata", None)
        if usage:
            input_tokens += usage.get("input_tokens", 0)
            output_tokens += usage.get("output_tokens", 0)
    total_tokens = input_tokens + output_tokens

    # Last message in the thread is the final AI response.
    final_message = result["messages"][-1]
    content = final_message.content if hasattr(final_message, "content") else str(final_message)
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    return content, tool_calls, {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
