import os
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from db import users_collection, leads_collection
from models.course_model import find_course_by_name, get_all_courses
from services.rag_service import retrieve_relevant_courses, build_context
from services.memory_service import get_history, append_message

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


EXACT_LIST_TRIGGERS = [
    "courses",
    "list courses",
    "show courses",
    "what courses",
    "available courses",
    "what do you offer",
    "what programs"
]


def is_lead_intent(message):
    return any(x in message for x in ["join", "enroll", "interested", "admission", "register"])


# AI with RAG + Memory
def ai_generate(phone, user_message):
    try:
        courses = retrieve_relevant_courses(user_message)

        if not courses:
            return "I can help you explore courses or guide you based on your goals. What are you interested in?"

        context = build_context(courses)
        history = get_history(phone)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly course advisor.\n"
                    "Speak naturally.\n"
                    "Guide users step by step.\n"
                    "Recommend best course.\n"
                    "Use ONLY provided data.\n\n"
                    f"{context}"
                )
            }
        ]

        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300  
        )

        reply = response.choices[0].message.content

        append_message(phone, "user", user_message)
        append_message(phone, "assistant", reply)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "Sorry, I’m having trouble answering right now."


def list_courses():
    courses = get_all_courses()
    return "We offer these courses:\n\n" + "\n".join([f"• {c['name'].title()}" for c in courses])


# Main handler
def handle_message(phone, message):
    raw_message = message
    message = message.lower().strip()

    user = users_collection.find_one({"phone": phone})

    # NEW USER
    if not user:
        users_collection.insert_one({
            "phone": phone,
            "step": "normal"
        })

        return (
            "Hi 👋 I’m your course assistant.\n"
            "I can help you choose the best course for your career.\n"
            "What would you like to learn?"
        )

    step = user.get("step", "normal")

    # GREETING
    if message in ["hi", "hello", "hey"]:
        return "Hi 👋 How can I help you today? You can ask about courses or career guidance."

    
    if message in EXACT_LIST_TRIGGERS:
        return list_courses()

    # LEAD CAPTURE 
    if step == "lead_capture":
        parts = [p.strip() for p in raw_message.split(",")]

        if len(parts) < 2:
            return "Please send details like: Name, Phone"

        name = parts[0]
        phone_no = parts[1]

        email = None
        for p in parts:
            if "@" in p:
                email = p

        lead = {
            "user_phone": phone,
            "name": name,
            "contact": phone_no,
            "email": email,
            "course": user.get("selected_course"),
            "status": "new",
            "created_at": datetime.utcnow() 
        }

        leads_collection.insert_one(lead)

        
        users_collection.update_one(
            {"phone": phone},
            {"$set": {"step": "normal"}}
        )

        return "🎉 Thank you! Our team will contact you shortly."

    # LEAD INTENT
    if is_lead_intent(message):
        users_collection.update_one(
            {"phone": phone},
            {"$set": {
                "step": "lead_capture",
                "selected_course": user.get("selected_course")  
            }}
        )

        return "Great! 😊 Please share your Name, Phone (comma separated)."

    
    if len(message) > 3 and step != "lead_capture":
        course = find_course_by_name(message)
        if course:
            users_collection.update_one(
                {"phone": phone},
                {"$set": {"selected_course": course["name"]}}
            )

            return (
                f"{course['name'].title()} Course:\n"
                f"Duration: {course['duration']}\n"
                f"Price: {course['price']}\n"
                f"{course['description']}\n\n"
                "If you're interested, just say 'I want to join' 😊"
            )

    # FINAL FALLBACK → AI
    return ai_generate(phone, raw_message)