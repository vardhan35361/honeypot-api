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


def safe_success():
    return {"status": "success"}


async def process(request: Request, x_api_key: Optional[str]):
    # API Key check (only if provided)
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Safe JSON parsing
    try:
        data = await request.json()
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    session_id = data.get("sessionId", "tester-session")
    message = data.get("message", {})
    text = str(message.get("text", "")).lower()

    if session_id not in sessions:
        sessions[session_id] = {"count": 0}

    sessions[session_id]["count"] += 1
    count = sessions[session_id]["count"]

    scam = any(keyword in text for keyword in SCAM_KEYWORDS)

    if scam and count < 3:
        reply = random.choice(CONFUSED_REPLIES)
    elif scam:
        reply = random.choice(HELPER_REPLIES)
    else:
        reply = "Okay."

    return {
        "status": "success",
        "scamDetected": scam,
        "messageCount": count,
        "reply": reply
    }


# GET endpoints (health check for Render)
@app.get("/")
async def root_get():
    return safe_success()


@app.get("/honeypot")
async def honeypot_get():
    return safe_success()


# POST endpoints
@app.post("/")
async def root_post(request: Request, x_api_key: Optional[str] = Header(None)):
    return await process(request, x_api_key)


@app.post("/honeypot")
async def honeypot_post(request: Request, x_api_key: Optional[str] = Header(None)):
    return await process(request, x_api_key)
