from fastapi import FastAPI, Header, HTTPException, Request, Body
from pydantic import BaseModel, Field
import os
import random
from typing import Optional, Any

app = FastAPI()

API_KEY = os.getenv("API_KEY", "mysecretkey")

SCAM_KEYWORDS = ["account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"]
CONFUSED_REPLIES = ["What is this message?", "I don’t understand this.", "Why am I getting this?"]
HELPER_REPLIES = ["Which bank is this?", "Why is this urgent?", "Can you explain properly?"]

# In-memory session storage (Note: will reset on server restart)
sessions = {}

# Define a Schema to handle flexible input
class MessageData(BaseModel):
    sessionId: Optional[str] = "tester-session"
    message: Optional[Any] = None  # Can be a dict or a string

def get_reply_logic(text: str, session_id: str):
    text = text.lower()
    if session_id not in sessions:
        sessions[session_id] = {"count": 0}

    sessions[session_id]["count"] += 1
    count = sessions[session_id]["count"]
    
    scam = any(k in text for k in SCAM_KEYWORDS)

    if scam and count < 3:
        reply = random.choice(CONFUSED_REPLIES)
    elif scam:
        reply = random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."
        
    return scam, count, reply

@app.get("/")
@app.get("/honeypot")
async def root_get():
    return {"status": "success"}

@app.post("/")
@app.post("/honeypot")
async def process_post(
    request: Request, 
    x_api_key: Optional[str] = Header(None),
    data: dict = Body(None) # Catch-all for varied JSON structures
):
    # 1. API Key Validation
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Extract Data Safely
    if data is None:
        data = {}

    session_id = data.get("sessionId", "tester-session")
    raw_msg = data.get("message", "")
    
    # Handle message if it's a dict {"text": "..."} or just a string "..."
    if isinstance(raw_msg, dict):
        text_content = str(raw_msg.get("text", ""))
    else:
        text_content = str(raw_msg)

    # 3. Process Logic
    scam_detected, count, reply = get_reply_logic(text_content, session_id)

    return {
        "status": "success",
        "scamDetected": scam_detected,
        "messageCount": count,
        "reply": reply
    }
