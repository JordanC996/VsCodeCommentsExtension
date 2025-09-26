from abc import ABC, abstractmethod
from model.comments import Comments, Comment
from llm_client.llm_client import LLMClient, OllamaClient
import json
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
        code_lines = code.splitlines()

        numbered_lines = [f"{i}: {line}" for i, line in enumerate(code_lines)]

        numbered_code = "\n".join(numbered_lines)

        user_prompt = prompts["user"].format(code=numbered_code)

        comments = Comments(
            **json.loads(
                self._llm_client.chat_completion(
                    prompts["system"], user_prompt, Comments
                )
            )
        )

        for comment in comments:
            code_lines.insert(comment.row, f"{comment.value}")

        return "\n".join(code_lines)

        # original_lines = [line.split(":", 1)[1] for line in numbered_lines]

        # original code without indices "".join(original_lines)


def get_comments_service() -> CommentsService:
    llm_client = OllamaClient(config["ollama"]["model"])
    return CommentsService(llm_client)
