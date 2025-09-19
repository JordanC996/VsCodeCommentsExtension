from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import ollama
app = FastAPI()

class Payload(BaseModel):
    text: str
    
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/process")
def process_text(payload: Payload):
    # Logica di elaborazione
    query = payload.text
    result = ollama.chat(model="gemma3:1b", messages=[
    {"role": "user", "content": query}
])
    return {"result": result['message']['content']}

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