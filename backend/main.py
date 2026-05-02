from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["chatbot_db"]

class ChatRequest(BaseModel):
    phone: str
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    user = db.users.find_one({"phone": req.phone})

    if not user:
        db.users.insert_one({
            "phone": req.phone,
            "step": "start"
        })
        return {"reply": "Hi 👋 I’m your assistant. How can I help you today?"}

    message = req.message.lower()

    if "course" in message:
        return {"reply": "We offer Python, Web Development, and Cloud Computing. Which one are you interested in?"}

    if "python" in message:
        return {"reply": "Python Course:\nDuration: 3 months\nPrice: ₹5000\nWould you like to book a demo?"}

    if "yes" in message:
        db.users.update_one({"phone": req.phone}, {"$set": {"step": "lead"}})
        return {"reply": "Please share your Name, Email, and Phone number."}

    if user.get("step") == "lead":
        db.leads.insert_one({
            "phone": req.phone,
            "details": req.message
        })
        return {"reply": "Thank you! Our team will contact you shortly."}

    return {"reply": "Sorry, I didn’t understand. Can you please rephrase?"}