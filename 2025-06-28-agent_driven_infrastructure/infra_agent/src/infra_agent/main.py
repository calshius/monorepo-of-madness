import os
from langgraph.agent import Agent, Tool, Skill

from infra_agent.clients.llm_client import HuggingFaceLLM
from infra_agent.clients.k8s_client import scale_k8s_deployment

WATCH_FILE = os.getenv("WATCH_FILE", "../../event_file.txt")

def check_for_change():
    """Check if the file indicates a change is incoming."""
    if not os.path.exists(WATCH_FILE):
        return False
    with open(WATCH_FILE) as f:
        content = f.read().strip()
    return content.lower() == "scale"

def get_desired_replicas(llm, prompt):
    """Ask the LLM for the desired replica count."""
    response = llm(prompt)
    # Try to extract an integer from the LLM's response
    for word in response.split():
        if word.isdigit():
            return int(word)
    # Default fallback
    return 1

# Define LangGraph tools/skills
scale_tool = Tool(
    name="scale_k8s",
    description="Scale a Kubernetes deployment",
    func=lambda ns, dep, rep: scale_k8s_deployment(ns, dep, int(rep)),
    args=["namespace", "deployment", "replicas"]
)

class InfraSkill(Skill):
    def __init__(self, llm):
        self.llm = llm

    def run(self, **kwargs):
        if check_for_change():
            prompt = (
                "A scaling event was detected. "
                "Based on current conditions, what should the new replica count be for the deployment? "
                "Reply with only the number."
            )
            replicas = get_desired_replicas(self.llm, prompt)
            return scale_k8s_deployment("callum-dev", "user-api", replicas)
        else:
            return scale_k8s_deployment("callum-dev", "user-api", 1)

def main():
    hf_token = os.getenv("HF_TOKEN")
    llm = HuggingFaceLLM(api_token=hf_token)
    agent = Agent(
        skills=[InfraSkill(llm)],
        tools=[scale_tool],
        llm=llm
    )
    
    # Example prompt to activate the agent
    prompt = "Check if a change is incoming and scale the deployment accordingly."
    result = agent.run(prompt=prompt)
    print(result)

if __name__ == "__main__":
    main()