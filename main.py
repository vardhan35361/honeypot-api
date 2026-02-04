from fastapi import FastAPI, Header, HTTPException, Request
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
async def handle_request(request: Request, x_api_key: str = Header(None)):
    # 1. API Key Check (Only if provided)
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Ultra-Robust Body Extraction
    # We use a try-except block to ensure we NEVER return a 422 or 500 error
    try:
        body = await request.json()
    except:
        body = {}

    # Ensure body is a dictionary
    if not isinstance(body, dict):
        body = {}

    # 3. Extract Session ID
    session_id = str(body.get("sessionId", "tester-session"))

    # 4. Extract Message Text (Handle both String and Dict styles)
    # This handles: {"message": "text"} AND {"message": {"text": "text"}}
    raw_message = body.get("message", "")
    if isinstance(raw_message, dict):
        message_text = str(raw_message.get("text", "")).lower()
    else:
        message_text = str(raw_message).lower()

    # 5. Logic
    if session_id not in sessions:
        sessions[session_id] = 0
    
    sessions[session_id] += 1
    count = sessions[session_id]
    
    is_scam = any(k in message_text for k in SCAM_KEYWORDS) if message_text else False

    # Determine Reply
    if is_scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    # 6. Final Response (Matches expected Honeypot format)
    return {
        "status": "success",
        "scamDetected": is_scam,
        "messageCount": count,
        "reply": reply
    }
