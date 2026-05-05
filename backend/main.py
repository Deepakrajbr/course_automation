from fastapi import FastAPI, Request
from fastapi.responses import Response
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


@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    phone = form.get("From", "").replace("whatsapp:", "")
    message = form.get("Body", "")

    reply = handle_message(phone, message)

    twiml = f"""
<Response>
    <Message>{reply}</Message>
</Response>
"""

    return Response(content=twiml, media_type="application/xml")