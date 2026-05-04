from db import conversations_collection

MAX_TURNS = 6

def get_history(phone):
    doc = conversations_collection.find_one({"phone": phone})
    return doc["messages"] if doc else []

def append_message(phone, role, content):
    doc = conversations_collection.find_one({"phone": phone})

    if not doc:
        conversations_collection.insert_one({
            "phone": phone,
            "messages": [{"role": role, "content": content}]
        })
        return

    messages = doc["messages"] + [{"role": role, "content": content}]
    messages = messages[-(MAX_TURNS * 2):]

    conversations_collection.update_one(
        {"phone": phone},
        {"$set": {"messages": messages}}
    )