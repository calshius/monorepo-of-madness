# Infra Agent

This agent monitors an event file for natural language messages describing expected infrastructure load or events. It uses a large language model (LLM) to interpret the message and decide whether to scale up, scale down, or make no changes to a Kubernetes deployment. If scaling is required, the agent can also use the LLM to determine the appropriate number of replicas and then applies the scaling action automatically to the specified deployment.

**Key features:**
- Reads human-friendly event descriptions from a file.
- Uses an LLM (e.g., Gemini) to classify intent: scale up, scale down, or no scale.
- Optionally asks the LLM for the desired replica count.
- Automatically scales a Kubernetes deployment based on the LLM's decision.

This enables natural language-driven, automated infrastructure scaling.