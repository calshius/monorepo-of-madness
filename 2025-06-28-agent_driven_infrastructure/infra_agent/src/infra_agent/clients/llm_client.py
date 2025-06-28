from huggingface_hub import InferenceClient

class HuggingFaceLLM:
    def __init__(self, api_token, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.client = InferenceClient(token=api_token)
        self.model = model

    def __call__(self, prompt):
        response = self.client.text_generation(prompt, model=self.model, max_new_tokens=128)
        return response