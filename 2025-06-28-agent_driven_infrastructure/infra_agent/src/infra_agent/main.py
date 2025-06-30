import os
import traceback
from langgraph.graph import StateGraph, END, START

from langchain_google_genai import ChatGoogleGenerativeAI
from infra_agent.clients.k8s_client import scale_k8s_deployment

WATCH_FILE = os.getenv("WATCH_FILE", "../../event_file.txt")


def check_for_change_node(state):
    if not os.path.exists(WATCH_FILE):
        return {**state, "action": "no_scale"}
    with open(WATCH_FILE) as f:
        content = f.read().strip()
    llm = state["llm"]
    prompt = (
        "You are an infrastructure agent. "
        "Given the following message, reply with only one of: scale_up, scale_down, or no_scale. "
        "Message: '''" + content + "'''"
    )
    try:
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            action = response.content.strip().lower()
        else:
            action = str(response).strip().lower()
        if action not in {"scale_up", "scale_down", "no_scale"}:
            action = "no_scale"
        # Only print the LLM's suggestion
        print(f"LLM suggested action: {action}")
        return {**state, "action": action}
    except Exception:
        return {**state, "action": "no_scale"}


def ask_llm_for_replicas_node(state):
    llm = state["llm"]
    prompt = (
        "A scaling event was detected for the 'user-api' deployment in the 'callum-dev' namespace. "
        "Based on current and expected conditions, how many replicas should this deployment have? "
        "Reply with only the number."
    )
    try:
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)
        for word in text.split():
            if word.isdigit():
                print(f"Replicas set to: {int(word)}")
                return {**state, "replicas": int(word)}
        print("Replicas set to: 2")
        return {**state, "replicas": 2}
    except Exception:
        print("Replicas set to: 2")
        return {**state, "replicas": 2}


def scale_deployment_node(state):
    replicas = state.get("replicas", 1)
    result = scale_k8s_deployment("callum-dev", "user-api", replicas)
    return {**state, "result": result}


def scale_down_node(state):
    replicas = 1
    result = scale_k8s_deployment("callum-dev", "user-api", replicas)
    print(f"Replicas set to: {replicas}")
    return {**state, "replicas": replicas, "result": result}


def main():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

    workflow = StateGraph(dict)
    workflow.add_node("check_for_change", check_for_change_node)
    workflow.add_node("ask_llm_for_replicas", ask_llm_for_replicas_node)
    workflow.add_node("scale_deployment", scale_deployment_node)
    workflow.add_node("scale_down", scale_down_node)
    workflow.add_edge(START, "check_for_change")
    workflow.add_conditional_edges(
        "check_for_change",
        lambda state: (
            "ask_llm_for_replicas" if state.get("action") == "scale_up"
            else "scale_down" if state.get("action") == "scale_down"
            else END
        ),
    )
    workflow.add_edge("ask_llm_for_replicas", "scale_deployment")
    workflow.add_edge("scale_deployment", END)
    workflow.add_edge("scale_down", END)

    app = workflow.compile()
    app.invoke({"llm": llm})


if __name__ == "__main__":
    main()
