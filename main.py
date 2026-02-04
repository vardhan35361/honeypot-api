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

# In-memory session store
sessions = {}

@app.get("/")
@app.get("/honeypot")
async def health_check():
    return {"status": "success"}

@app.post("/")
@app.post("/honeypot")
async def handle_honeypot(request: Request, x_api_key: str = Header(None)):
    # 1. API Key Check
    if x_api_key and x_api_key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    # 2. Ultra-Safe Body Parsing (The "Invincible" Part)
    data = {}
    try:
        # Read raw bytes first to avoid crash on empty body
        body_bytes = await request.body()
        if body_bytes:
            # Manually try to parse JSON
            data = await request.json()
    except:
        # If body is empty or not JSON, just act like it's empty
        data = {}

    # Force data to be a dict if it parsed as a list/string
    if not isinstance(data, dict):
        data = {}

    # 3. Extract Session and Message safely
    # Check for camelCase 'sessionId' and snake_case 'session_id'
    session_id = str(data.get("sessionId", data.get("session_id", "tester-session")))
    
    raw_message = data.get("message", "")
    message_text = ""

    if isinstance(raw_message, dict):
        message_text = str(raw_message.get("text", "")).lower()
    else:
        message_text = str(raw_message).lower()

    # 4. Session Counter
    if session_id not in sessions:
        sessions[session_id] = 0
    sessions[session_id] += 1
    count = sessions[session_id]

    # 5. Scam Detection Logic
    scam = any(k in message_text for k in SCAM_KEYWORDS) if message_text else False

    if scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    # 6. Final JSON Response
    return {
        "status": "success",
        "scamDetected": scam,
        "messageCount": count,
        "reply": reply
    }
