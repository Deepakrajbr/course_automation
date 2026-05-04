from db import courses_collection

def get_all_courses():
    return list(courses_collection.find({}, {"_id": 0}))

def find_course_by_name(name):
    return courses_collection.find_one({
        "name": {"$regex": name, "$options": "i"}
    })