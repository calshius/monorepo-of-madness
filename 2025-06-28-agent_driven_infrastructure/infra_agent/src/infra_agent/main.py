import os
import traceback
from langgraph.graph import StateGraph, END, START

from infra_agent.clients.llm_client import HuggingFaceLLM
from infra_agent.clients.k8s_client import scale_k8s_deployment

WATCH_FILE = os.getenv("WATCH_FILE", "../../event_file.txt")


def check_for_change_node(state):
    print("Running check_for_change_node with state:", state)
    if not os.path.exists(WATCH_FILE):
        return {**state, "change": False}
    with open(WATCH_FILE) as f:
        content = f.read().strip()
    result = {**state, "change": "scale" in content.lower()}
    print("check_for_change_node result:", result)
    return result


def ask_llm_for_replicas_node(state):
    print("Running ask_llm_for_replicas_node with state:", state)
    llm = state["llm"]
    prompt = (
        "A scaling event was detected for the 'user-api' deployment in the 'callum-dev' namespace. "
        "Based on current and expected conditions, how many replicas should this deployment have? "
        "Reply with only the number."
    )
    try:
        response = llm(prompt)
        print("LLM response:", response)
        for word in response.split():
            if word.isdigit():
                result = {**state, "replicas": int(word)}
                print("ask_llm_for_replicas_node result:", result)
                return result
        print("LLM did not return a number, defaulting to 1 replica.")
        return {**state, "replicas": 1}
    except Exception as e:
        print("Error in ask_llm_for_replicas_node:", e)
        traceback.print_exc()
        return {**state, "replicas": 1}


def scale_deployment_node(state):
    replicas = state.get("replicas", 1)
    result = scale_k8s_deployment("callum-dev", "user-api", replicas)
    return {**state, "result": result}


def scale_to_one_node(state):
    result = scale_k8s_deployment("callum-dev", "user-api", 1)
    return {**state, "result": result}


def main():
    hf_token = os.getenv("HF_TOKEN")
    llm = HuggingFaceLLM(api_token=hf_token)

    workflow = StateGraph(dict)
    workflow.add_node("check_for_change", check_for_change_node)
    workflow.add_node("ask_llm_for_replicas", ask_llm_for_replicas_node)
    workflow.add_node("scale_deployment", scale_deployment_node)
    workflow.add_node("scale_to_one", scale_to_one_node)
    workflow.add_edge(START, "check_for_change")
    workflow.add_conditional_edges(
        "check_for_change",
        lambda state: "ask_llm_for_replicas" if state["change"] else "scale_to_one",
    )
    workflow.add_edge("ask_llm_for_replicas", "scale_deployment")
    workflow.add_edge("scale_deployment", END)
    workflow.add_edge("scale_to_one", END)

    app = workflow.compile()
    result = app.invoke({"llm": llm})
    print("Final workflow result:", result)


if __name__ == "__main__":
    main()
