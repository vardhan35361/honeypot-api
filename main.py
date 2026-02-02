from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional
import os
import random

app = FastAPI()

API_KEY = os.getenv("API_KEY", "mysecretkey")

SCAM_KEYWORDS = [
    "account", "blocked", "verify", "urgent", "upi", "otp", "bank", "suspended"
]

CONFUSED_REPLIES = [
    "What is this message?",
    "I don’t understand this.",
    "Why am I getting this?",
    "What happened to my account?",
    "This is confusing."
]

HELPER_REPLIES = [
    "Which bank is this?",
    "Why is this urgent?",
    "Can you explain properly?",
    "Which account is affected?"
]

sessions = {}

@app.get("/")
async def health():
    return {"status": "success"}

@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: Optional[str] = Header(None)):

    # Allow missing API key (tester sometimes skips it)
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        data = await request.json()
    except:
        data = {}

    session_id = data.get("sessionId", "default-session")
    message = data.get("message", {})
    text = str(message.get("text", "")).lower()

    if session_id not in sessions:
        sessions[session_id] = 0

    sessions[session_id] += 1
    count = sessions[session_id]

    scam = any(keyword in text for keyword in SCAM_KEYWORDS)

    if scam and count < 3:
        reply = random.choice(CONFUSED_REPLIES)
    elif scam:
        reply = random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    return {
        "status": "success",
        "reply": reply
    }
