from abc import ABC, abstractmethod
from model.comments import Comments
from llm_client import LLMClient
import ollama
import yaml
import os

with open(os.environ["PROMPTS_PATH"], "r") as f:
    prompts = yaml.safe_load(f)

with open(os.environ["CONFIG_PATH"], "r") as f:
    config = yaml.safe_load(f)


class ICommentsService(ABC):
    @abstractmethod
    def get_comments(code: str):
        pass


class CommentsService(ICommentsService):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def get_comments(self, code: str):
        code_lines = code.splitlines(keepends=True)

        numbered_lines = [f"{i}: {line}" for i, line in enumerate(code_lines)]

        numbered_code = "".join(numbered_lines)

        user_prompt = prompts["user"].format(code=numbered_code)

        comments = self._llm_client.chat_completion(
            prompts["system"], user_prompt, Comments
        )

        # original_lines = [line.split(":", 1)[1] for line in numbered_lines]

        # original code without indices "".join(original_lines)
