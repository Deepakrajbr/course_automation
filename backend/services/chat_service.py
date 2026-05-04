import os
from openai import OpenAI
from dotenv import load_dotenv

from db import users_collection, leads_collection
from models.course_model import find_course_by_name, get_all_courses
from services.rag_service import retrieve_relevant_courses, build_context
from services.memory_service import get_history, append_message

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🔥 INTENT: lead detection (simple + powerful)
def is_lead_intent(message):
    msg = message.lower()
    return any(x in msg for x in ["join", "enroll", "interested", "admission", "register"])


# 🤖 AI with RAG + MEMORY (IMPROVED)
def ai_generate(phone, user_message):
    try:
        # 🔎 RAG
        courses = retrieve_relevant_courses(user_message)

        # 🚨 if nothing found
        if not courses:
            return "Sorry, I couldn't find relevant course info. Can you be more specific?"

        context = build_context(courses)

        # 🧠 MEMORY
        history = get_history(phone)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly course advisor.\n"
                    "Speak naturally like a human.\n"
                    "Guide users step by step.\n"
                    "Use previous conversation context.\n"
                    "Understand user intent.\n"
                    "Recommend best course based on needs.\n"
                    "ONLY use COURSE DATA below.\n"
                    "If answer not found, say you don't know.\n\n"
                    f"COURSE DATA:\n{context}"
                )
            }
        ]

        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150
        )

        reply = response.choices[0].message.content

        # 🧠 save memory
        append_message(phone, "user", user_message)
        append_message(phone, "assistant", reply)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "Sorry, I’m having trouble answering right now."


# 📋 List courses (small improvement)
def list_courses():
    courses = get_all_courses()
    return "We offer these courses:\n\n" + "\n".join([f"• {c['name'].title()}" for c in courses])


# 🧠 MAIN HANDLER (RAG-FIRST LOGIC)
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

    # 🔥 STEP: LEAD CAPTURE
    if step == "lead_capture":
        if "," not in raw_message:
            return "Please send details like: Name, Phone"

        parts = raw_message.split(",")

        lead = {
            "user_phone": phone,
            "name": parts[0].strip(),
            "contact": parts[1].strip() if len(parts) > 1 else "",
            "course": user.get("selected_course"),
            "status": "new"
        }

        leads_collection.insert_one(lead)

        users_collection.update_one(
            {"phone": phone},
            {"$set": {"step": "done"}}
        )

        return "🎉 Thank you! Our team will contact you shortly."

    # 🔥 LEAD INTENT
    if is_lead_intent(message):
        users_collection.update_one(
            {"phone": phone},
            {"$set": {"step": "lead_capture"}}
        )

        return "Great! 😊 Please share your Name and Phone (comma separated)."

    # 🔥 OPTIONAL: course list trigger (soft match)
    if any(x in message for x in ["course", "program", "learn", "study"]):
        return list_courses()

    # 🔥 COURSE MATCH (quick path)
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

    # 🔥 DEFAULT → RAG handles everything
    return ai_generate(phone, raw_message)