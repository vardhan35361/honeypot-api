from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import random

app = FastAPI()

# Configuration
API_KEY = os.getenv("API_KEY", "mysecretkey")
SCAM_KEYWORDS = ["account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"]
CONFUSED_REPLIES = ["What is this message?", "I don’t understand this.", "Why am I getting this?"]
HELPER_REPLIES = ["Which bank is this?", "Why is this urgent?", "Can you explain properly?"]

# Persistence
sessions = {}

@app.get("/")
@app.get("/honeypot")
async def health_check():
    return {"status": "success"}

@app.post("/")
@app.post("/honeypot")
async def handle_all_posts(request: Request, x_api_key: str = Header(None)):
    # 1. Auth Check
    if x_api_key and x_api_key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    # 2. The "Safety Net" for Request Body
    data = {}
    try:
        # Check if the body exists before parsing
        body_bytes = await request.body()
        if body_bytes:
            data = await request.json()
    except Exception:
        # If the body is empty or not JSON, we just use an empty dict
        data = {}

    # Ensure data is actually a dictionary
    if not isinstance(data, dict):
        data = {}

    # 3. Safe Extraction (Handles sessionId/session_id/message/message.text)
    session_id = str(data.get("sessionId", data.get("session_id", "tester-session")))
    
    raw_msg = data.get("message", "")
    if isinstance(raw_msg, dict):
        text = str(raw_msg.get("text", "")).lower()
    else:
        text = str(raw_msg).lower()

    # 4. Logic & Session Management
    if session_id not in sessions:
        sessions[session_id] = 0
    
    sessions[session_id] += 1
    count = sessions[session_id]

    # Scam Logic
    is_scam = any(k in text for k in SCAM_KEYWORDS) if text else False

    if is_scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    # 5. Guaranteed JSON Response
    return {
        "status": "success",
        "scamDetected": is_scam,
        "messageCount": count,
        "reply": reply
    }
