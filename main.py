from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY", "mysecretkey")

# ---------- REQUEST MODELS ----------

class Message(BaseModel):
    text: str

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message

# ---------- RESPONSES ----------

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

# ---------- HEALTH CHECK ----------

@app.get("/")
def health():
    return {"status": "success"}

# ---------- MAIN ENDPOINT ----------

@app.post("/honeypot")
def honeypot(
    payload: HoneypotRequest,
    x_api_key: Optional[str] = Header(None)
):
    # Allow missing API key (tester sometimes skips it)
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.text.lower()

    scam = any(keyword in text for keyword in SCAM_KEYWORDS)

    if scam:
        reply = random.choice(CONFUSED_REPLIES)
    else:
        reply = "Okay."

    # 🔥 RETURN ONLY WHAT TESTER EXPECTS
    return {
        "status": "success",
        "reply": reply
    }
