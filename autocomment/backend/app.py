import os
config_path = os.getcwd() + os.sep + "autocomment" + os.sep + "backend" + os.sep +  "config"

os.environ["CONFIG_PATH"] = config_path + os.sep + "config.yaml"

os.environ["PROMPTS_PATH"] = config_path + os.sep + "prompts.yaml"

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from service.comments_service import CommentsService, get_comments_service
from fastapi.responses import StreamingResponse
import ollama



app = FastAPI()


class Payload(BaseModel):
    text: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/process")
def process_text(
    payload: Payload, comments_service: CommentsService = Depends(get_comments_service)
):
    # Logica di elaborazione
    query = payload.text
    result = comments_service.get_comments(query)
    return {"result": result["message"]["content"]}


@app.post("/process_old")
def process_text(payload: Payload):
    # Logica di elaborazione
    query = payload.text
    result = ollama.chat(
        model="gemma3:1b", messages=[{"role": "user", "content": query}]
    )
    return {"result": result["message"]["content"]}


@app.post("/chat")
async def chat_endpoint(prompt: Payload):
    def generate():
        stream = ollama.chat(
            model="gemma3:1b",
            messages=[{"role": "user", "content": prompt.text}],
            stream=True,
        )
        for chunk in stream:
            yield chunk["message"]["content"]

    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",              # se il file si chiama main.py
        host="0.0.0.0",
        port=8000,
        reload=True
    )