from fastapi import FastAPI
from pydantic import BaseModel
from services.chat_service import handle_message

app = FastAPI()


class ChatRequest(BaseModel):
    phone: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    reply = handle_message(req.phone, req.message)
    return {"reply": reply}