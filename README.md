#  WhatsApp AI Enquiry Assistant

An AI-powered WhatsApp chatbot designed for educational institutions to handle student enquiries, provide course details, and capture leads in real-time.

---

##  Problem Statement

Educational institutions often struggle to:
- Handle large volumes of student queries
- Provide consistent course information
- Capture and follow up with leads efficiently

This project solves these challenges using automation + AI.

---

##  Solution

This system uses a WhatsApp-based interface to:
- Answer student queries
- Recommend relevant courses
- Capture lead details
- Enable follow-up by admin

---

##  Architecture
User (WhatsApp)
↓
Twilio (Webhook)
↓
n8n (Workflow Automation)
↓
FastAPI Backend (Controller)
↓
Service Layer:

Chat Logic
RAG (Retrieval Augmented Generation)
Memory (Conversation Context)
↓
MongoDB (Database)
↓
Response → WhatsApp


---

##  Key Features

-  **WhatsApp Integration** via Twilio
-  **Workflow Automation** using n8n
-  **AI-powered responses** (RAG-based)
-  **Conversation Memory** (context-aware replies)
-  **Lead Capture System**
-  **MongoDB-based knowledge base**

---

##  Tech Stack

- Backend: FastAPI (Python)
- Database: MongoDB
- Automation: n8n
- Messaging: Twilio WhatsApp API
- AI: RAG (Embeddings + Semantic Search)
- Optional AI Providers:
  - OpenAI
  - Hugging Face

---

##  How RAG Works

1. User sends a query  
2. Query is converted into embeddings  
3. Compared with course data (cosine similarity)  
4. Top relevant courses retrieved  
5. Context passed to AI for response generation  

---

##  Conversation Flow

1. User says "Hi"  
2. Bot responds naturally  
3. User asks about courses  
4. Bot recommends relevant course  
5. User selects course  
6. Bot shares details  
7. User books demo  
8. Lead stored in database  

---



