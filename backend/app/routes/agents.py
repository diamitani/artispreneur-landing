"""POST /agent/chat, GET /agent/status"""
from fastapi import APIRouter, Depends
from app.models import ChatRequest
from app.auth import get_user
from app.agents import chat
from app.db import fetch_all

router = APIRouter()


@router.post("/chat")
def agent_chat(req: ChatRequest, user: str = Depends(get_user)):
    reply = chat(req.message, req.agent_type)
    return {"reply": reply, "agent_type": req.agent_type}


@router.get("/status")
def agent_status(user: str = Depends(get_user)):
    agents = fetch_all(
        "SELECT agent_type, status FROM agent_sessions WHERE user_id=(SELECT id FROM workspace_users WHERE cognito_sub=%s)",
        (user,),
    )
    return {"agents": agents}
