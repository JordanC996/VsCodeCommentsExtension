from abc import ABC, abstractmethod
from pydantic import BaseModel
import ollama


class LLMClient(ABC):
    @abstractmethod
    def chat_completion(
        self, system_prompt: str, user_prompt: str, response_format: BaseModel
    ):
        pass


class OllamaClient(LLMClient):
    def __init__(self, model: str):
        self._model = model

    def chat_completion(self, system_prompt, user_prompt, response_format):
        response = ollama.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=self._model,
            format=response_format.model_json_schema(),
        )

        return response.message.content
