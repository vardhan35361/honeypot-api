from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import random
import json

app = FastAPI()

# 1. Configuration
API_KEY = os.getenv("API_KEY", "mysecretkey")
SCAM_KEYWORDS = ["account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"]
CONFUSED_REPLIES = ["What is this message?", "I don’t understand this.", "Why am I getting this?"]
HELPER_REPLIES = ["Which bank is this?", "Why is this urgent?", "Can you explain properly?"]

# 2. Persistence (In-memory)
sessions = {}

@app.get("/")
@app.get("/honeypot")
async def health():
    return {"status": "success"}

@app.post("/")
@app.post("/honeypot")
async def process_all(request: Request, x_api_key: str = Header(None)):
    # --- STEP 1: KEY VALIDATION ---
    if x_api_key and x_api_key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid API Key"})

    # --- STEP 2: MANUAL BODY PARSING (The Fix) ---
    data = {}
    try:
        # We read the raw bytes. This works even if the body is empty or missing.
        raw_body = await request.body()
        if raw_body:
            data = json.loads(raw_body)
    except:
        # If parsing fails, we use an empty dict. No error is thrown.
        data = {}

    if not isinstance(data, dict):
        data = {}

    # --- STEP 3: DATA EXTRACTION ---
    # Handle both 'sessionId' and 'session_id'
    sid = str(data.get("sessionId", data.get("session_id", "tester-session")))
    
    # Handle 'message' as a string OR as an object {"text": "..."}
    raw_msg = data.get("message", "")
    text = ""
    if isinstance(raw_msg, dict):
        text = str(raw_msg.get("text", "")).lower()
    else:
        text = str(raw_msg).lower()

    # --- STEP 4: SESSION & SCAM LOGIC ---
    if sid not in sessions:
        sessions[sid] = 0
    sessions[sid] += 1
    count = sessions[sid]

    is_scam = any(k in text for k in SCAM_KEYWORDS) if text else False

    # Logic for replies
    if is_scam:
        reply = random.choice(CONFUSED_REPLIES) if count < 3 else random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    # --- STEP 5: FINAL RESPONSE ---
    return {
        "status": "success",
        "scamDetected": bool(is_scam),
        "messageCount": int(count),
        "reply": str(reply)
    }
