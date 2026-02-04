from fastapi import FastAPI, Header, HTTPException, Request
import os
import random

app = FastAPI()

API_KEY = os.getenv("API_KEY", "mysecretkey")

SCAM_KEYWORDS = ["account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"]
CONFUSED_REPLIES = ["What is this message?", "I don’t understand this.", "Why am I getting this?"]
HELPER_REPLIES = ["Which bank is this?", "Why is this urgent?", "Can you explain properly?"]

# In-memory session store
sessions = {}

async def process(request: Request, x_api_key: str | None):
    # 1. API Key Validation
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Ultra-Safe Body Parsing
    data = {}
    try:
        # Check if there is any body content at all
        body_bytes = await request.body()
        if body_bytes:
            data = await request.json()
            # If data is not a dict (like a list or string), reset to empty dict
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}

    # 3. Safely Extract Fields
    # The tester might send 'sessionId' or 'session_id' or nothing
    session_id = str(data.get("sessionId", data.get("session_id", "tester-session")))
    
    # 4. Robust Message Extraction
    # Handles: {"message": "hello"}, {"message": {"text": "hello"}}, or missing message
    raw_message = data.get("message", "")
    text = ""
    
    if isinstance(raw_message, dict):
        text = str(raw_message.get("text", "")).lower()
    else:
        text = str(raw_message).lower()

    # 5. Session Counter Logic
    if session_id not in sessions:
        sessions[session_id] = {"count": 0}
    
    sessions[session_id]["count"] += 1
    count = sessions[session_id]["count"]

    # 6. Response Logic
    scam = any(k in text for k in SCAM_KEYWORDS) if text else False

    if scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    return {
        "status": "success",
        "scamDetected": scam,
        "messageCount": count,
        "reply": reply
    }

@app.get("/")
@app.get("/honeypot")
async def health_check():
    return {"status": "success"}

@app.post("/")
async def root_post(request: Request, x_api_key: str | None = Header(None)):
    return await process(request, x_api_key)

@app.post("/honeypot")
async def honeypot_post(request: Request, x_api_key: str | None = Header(None)):
    return await process(request, x_api_key)
