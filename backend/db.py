import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["enquiry_bot"]

users_collection = db["users"]
leads_collection = db["leads"]
courses_collection = db["courses"]
conversations_collection = db["conversations"]