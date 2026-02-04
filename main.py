from fastapi import FastAPI, Header, Request, Query
from fastapi.responses import JSONResponse
import os
import random
import json

app = FastAPI()

# 1. Config
API_KEY = os.getenv("API_KEY", "mysecretkey")
SCAM_KEYWORDS = ["account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"]
CONFUSED_REPLIES = ["What is this message?", "I don’t understand this.", "Why am I getting this?"]
HELPER_REPLIES = ["Which bank is this?", "Why is this urgent?", "Can you explain properly?"]

sessions = {}

@app.get("/")
@app.get("/honeypot")
async def root_get():
    return {"status": "success"}

@app.post("/")
@app.post("/honeypot")
async def process_request(
    request: Request, 
    x_api_key: str = Header(None),
    sessionId: str = Query(None) # Check if sessionId is in the URL ?sessionId=xxx
):
    # 1. Check API Key
    if x_api_key and x_api_key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    # 2. Extract Data (The "Bulletproof" way)
    data = {}
    try:
        # Check if there is a body at all
        body_bytes = await request.body()
        if body_bytes:
            data = json.loads(body_bytes)
    except:
        data = {}

    # Ensure we are working with a dict
    if not isinstance(data, dict):
        data = {}

    # 3. Resolve Session ID (Check body first, then URL, then default)
    sid = data.get("sessionId", data.get("session_id", sessionId or "tester-session"))
    
    # 4. Resolve Message
    raw_msg = data.get("message", "")
    text = ""
    if isinstance(raw_msg, dict):
        text = str(raw_msg.get("text", "")).lower()
    else:
        text = str(raw_msg).lower()

    # 5. Counter Logic
    if sid not in sessions:
        sessions[sid] = 0
    sessions[sid] += 1
    count = sessions[sid]

    # 6. Scam Logic
    is_scam = any(k in text for k in SCAM_KEYWORDS) if text else False
    
    if is_scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    # 7. Final Response
    return {
        "status": "success",
        "scamDetected": bool(is_scam),
        "messageCount": int(count),
        "reply": str(reply)
    }
