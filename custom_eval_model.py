import os
from pydantic import BaseModel
from deepeval.models.base_model import DeepEvalBaseLLM
import requests

class LocalOllamaModel(DeepEvalBaseLLM):
    def __init__(self, model_name: str, url: str = "http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.url = url
        # Define standard headers for ngrok/cloud connection
        self.headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "DrPromptEval/1.0"
        }

    def load_model(self):
        return self.model_name

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                headers=self.headers,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"Error calling LLM for eval: {e}")
            return ""

    async def a_generate(self, prompt: str) -> str:
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False
                    },
                    headers=self.headers,
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            print(f"Error calling LLM for eval (async): {e}")
            return ""

    def get_model_name(self):
        return self.model_name
