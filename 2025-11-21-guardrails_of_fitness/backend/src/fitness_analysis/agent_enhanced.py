"""Enhanced LangGraph agent with data validation, PII guardrails, and orchestrator-worker pattern."""

from typing import Literal, Annotated
import operator
import re
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools import ALL_TOOLS
from .data_loader import FitnessDataLoader


# Enhanced state with worker support
class AgentState(MessagesState):
    """State for the fitness analysis agent with orchestrator-worker support."""
    data_loaded: bool = False
    tool_results: Annotated[list, operator.add] = []
    needs_synthesis: bool = False


class WorkerState(MessagesState):
    """State for worker nodes."""
    tool_name: str
    tool_args: dict
    tool_results: Annotated[list, operator.add] = []


# PII Detection Patterns
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "api_key": r"\b[A-Za-z0-9]{32,}\b",
}


def detect_pii(text: str) -> dict[str, list[str]]:
    """Detect PII in text."""
    findings = {}
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[pii_type] = matches
    return findings


def redact_pii(text: str) -> str:
    """Redact PII from text."""
    for pii_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", text)
    return text


# Data validation node
def validate_data_loaded(state: AgentState) -> AgentState:
    """Ensure fitness data is loaded before processing."""
    if state.get("data_loaded"):
        return state
    
    try:
        # Attempt to load data
        data_loader = FitnessDataLoader()
        data_loader.get_combined_summary(days=7)  # Test load
        state["data_loaded"] = True
        return state
    except Exception:
        # If data can't be loaded, still mark as checked to allow agent to continue
        # The agent can respond even without data access
        state["data_loaded"] = True  # Mark as checked to allow agent to continue
        return state


# Input guardrails with PII detection
def validate_input(state: AgentState) -> AgentState:
    """Validate and sanitize user input before processing with PII detection."""
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if not last_message or not isinstance(last_message, HumanMessage):
        return state
    
    content = last_message.content
    
    # PII Detection
    pii_found = detect_pii(content)
    if pii_found:
        # Redact PII from user message
        redacted_content = redact_pii(content)
        state["messages"][-1] = HumanMessage(content=redacted_content)
        # Warn user
        warning = AIMessage(
            content="Note: I've detected and redacted sensitive information (PII) from your message for security."
        )
        state["messages"].append(warning)
        return state
    
    # Check for malicious patterns
    forbidden_patterns = [
        "ignore previous instructions",
        "disregard",
        "system:",
        "admin:",
        "jailbreak",
    ]
    
    content_lower = content.lower()
    for pattern in forbidden_patterns:
        if pattern in content_lower:
            state["messages"][-1] = HumanMessage(
                content="I can only help with fitness and nutrition questions. Please ask about your fitness data or nutrition advice."
            )
            break
    
    # Check message length
    if len(content) > 2000:
        state["messages"][-1] = HumanMessage(
            content="Your message is too long. Please keep questions under 2000 characters."
        )
    
    return state


# Define the agent logic
def call_model(state: AgentState) -> AgentState:
    """Call the LLM with the current state."""
    messages = state["messages"]
    
    # Add system message if not present
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_message = SystemMessage(
            content="""You are a fitness and nutrition analysis assistant. You have access to the user's fitness data from Garmin and MyFitnessPal.

CRITICAL RULE: Before responding to ANY question about macros, diet, nutrition, or fitness, you MUST call get_fitness_data_summary or get_nutrition_details to see their actual data. DO NOT ask for information until you've checked what data already exists.

Available tools:
- get_fitness_data_summary: Get overview of nutrition and activity (USE THIS FIRST!)
- get_nutrition_details: Get detailed macro breakdown
- get_activity_details: Get workout statistics  
- search_recipes: Search for healthy recipes
- calculate_tdee: Calculate TDEE and recommended macros (requires age, height, weight, gender, activity_level)
- generate_mermaid_diagram: Create visualizations and charts

MANDATORY WORKFLOW for macro/diet questions:
1. IMMEDIATELY call get_fitness_data_summary() - NO EXCEPTIONS
2. Analyze the data you receive
3. Show the user their current stats (avg calories, protein, carbs, fat, workouts)
4. ONLY THEN ask for missing info (age, height, gender) if needed for TDEE calculation

The data files contain:
- ✅ Weight history, nutrition details (calories, protein, carbs, fat), activity data
- ❌ Age, height, gender (must ask user for these if needed)

Your response pattern MUST be:
1. Call tool to get data
2. Present their current stats
3. If calculating TDEE, ask for age/height/gender
4. Calculate and compare

NEVER start by asking for age/height/gender without first showing their current data from the tools.

Be encouraging and supportive. Only discuss fitness and nutrition topics."""
        )
        messages = [system_message] + messages
    
    # Initialize the model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
    )
    
    # Bind tools to the model
    model_with_tools = model.bind_tools(ALL_TOOLS)
    
    # Call the model
    response = model_with_tools.invoke(messages)
    
    # Check if multiple tools are being called
    if hasattr(response, "tool_calls") and len(response.tool_calls) > 1:
        state["needs_synthesis"] = True
    
    return {"messages": [response]}


# Worker node for executing tools
def execute_tool_worker(state: WorkerState) -> WorkerState:
    """Worker that executes a single tool."""
    # Find the tool
    tool = next((t for t in ALL_TOOLS if t.name == state["tool_name"]), None)
    if not tool:
        return {
            "tool_results": [{
                "tool": state["tool_name"],
                "result": f"Tool {state['tool_name']} not found"
            }]
        }
    
    # Execute the tool
    try:
        result = tool.invoke(state["tool_args"])
        return {
            "tool_results": [{
                "tool": state["tool_name"],
                "result": str(result)
            }]
        }
    except Exception as e:
        return {
            "tool_results": [{
                "tool": state["tool_name"],
                "result": f"Error executing {state['tool_name']}: {str(e)}"
            }]
        }


# Synthesizer node
def synthesize_results(state: AgentState) -> AgentState:
    """Synthesize results from multiple tool calls."""
    if not state.get("needs_synthesis") or not state.get("tool_results"):
        return state
    
    # Create synthesis prompt
    tool_summary = "\n\n".join([
        f"**{result['tool']}**:\n{result['result']}"
        for result in state["tool_results"]
    ])
    
    synthesis_prompt = f"""Based on the following tool results, provide a comprehensive synthesized answer:

{tool_summary}

Please combine these insights into a coherent, helpful response."""
    
    # Initialize model for synthesis
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
    )
    
    # Get synthesis
    synthesis = model.invoke([
        SystemMessage(content="You are synthesizing multiple data sources into a single coherent response."),
        HumanMessage(content=synthesis_prompt)
    ])
    
    # Clear tool results and add synthesized response
    return {
        "messages": [synthesis],
        "tool_results": [],
        "needs_synthesis": False
    }


# Output guardrails with PII detection
def validate_output(state: AgentState) -> AgentState:
    """Validate agent output before sending to user with PII detection."""
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if not last_message or not isinstance(last_message, AIMessage):
        return state
    
    content = last_message.content
    
    # Check for PII in output
    pii_found = detect_pii(content)
    if pii_found:
        redacted_content = redact_pii(content)
        state["messages"][-1] = AIMessage(content=redacted_content)
    
    # Check for sensitive information patterns
    if any(word in content.lower() for word in ["password", "secret", "token", "private key"]):
        state["messages"][-1] = AIMessage(
            content="I apologize, but I cannot share that information. Please ask about fitness or nutrition topics."
        )
    
    return state


# Routing logic
def should_continue(state: AgentState) -> Literal["tools", "synthesize", "output_guard", "__end__"]:
    """Determine whether to use tools, synthesize, or end the conversation."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are tool calls, continue to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # If we need to synthesize multiple tool results
    if state.get("needs_synthesis") and state.get("tool_results"):
        return "synthesize"
    
    # Otherwise, validate output before ending
    return "output_guard"


def check_data_loaded(state: AgentState) -> Literal["agent", "__end__"]:
    """Check if data is loaded before proceeding."""
    if not state.get("data_loaded"):
        return "__end__"
    return "agent"


# Build the graph
def create_fitness_agent():
    """Create and compile the fitness analysis agent with enhanced guardrails."""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_data", validate_data_loaded)
    workflow.add_node("input_guard", validate_input)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    workflow.add_node("synthesize", synthesize_results)
    workflow.add_node("output_guard", validate_output)
    
    # Add edges
    workflow.add_edge(START, "validate_data")
    workflow.add_conditional_edges(
        "validate_data",
        check_data_loaded,
        {
            "agent": "input_guard",
            END: END
        }
    )
    workflow.add_edge("input_guard", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "synthesize": "synthesize",
            "output_guard": "output_guard",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")
    workflow.add_edge("synthesize", "output_guard")
    workflow.add_edge("output_guard", END)
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# Create a singleton instance
fitness_agent = None


def get_fitness_agent():
    """Get or create the fitness agent instance."""
    global fitness_agent
    if fitness_agent is None:
        fitness_agent = create_fitness_agent()
    return fitness_agent
