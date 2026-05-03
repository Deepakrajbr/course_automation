import json
from db import users_collection, leads_collection

# load course data
with open("data/courses.json") as f:
    courses = json.load(f)


def find_course(name):
    for course in courses:
        if course["name"] in name.lower():
            return course
    return None


def handle_message(phone, message):
    message = message.lower().strip()

    user = users_collection.find_one({"phone": phone})

    # new user
    if not user:
        users_collection.insert_one({
            "phone": phone,
            "step": "choose_course"
        })
        return "Hi  I’m your assistant. We offer Python, Web Development, and Cloud courses.\nWhich one are you interested in?"

    step = user.get("step")

    # STEP 1: choose course
    if step == "choose_course":
        course = find_course(message)

        if course:
            users_collection.update_one(
                {"phone": phone},
                {"$set": {
                    "step": "confirm_demo",
                    "selected_course": course["name"]
                }}
            )

            return (
                f"{course['name'].title()} Course:\n"
                f"Duration: {course['duration']}\n"
                f"Price: {course['price']}\n"
                f"{course['description']}\n\n"
                "Would you like to book a demo? (yes/no)"
            )

        return "Please choose a valid course: Python, Web Development, or Cloud Computing."

    # STEP 2: confirm demo
    elif step == "confirm_demo":
        if "yes" in message:
            users_collection.update_one(
                {"phone": phone},
                {"$set": {"step": "lead_capture"}}
            )
            return "Great! Please share your Name, Email, and Phone number."

        return "No problem 🙂 Let me know if you need anything else."

    # STEP 3: lead capture
    elif step == "lead_capture":
        leads_collection.insert_one({
            "phone": phone,
            "details": message,
            "course": user.get("selected_course")
        })

        users_collection.update_one(
            {"phone": phone},
            {"$set": {"step": "done"}}
        )

        return "Thank you! Our team will contact you soon to schedule your demo."

    # fallback
    return "I didn't understand that. Please type a course name like Python or Web Development."