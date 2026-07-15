"""POST /auth/signup, POST /auth/login"""
from fastapi import APIRouter, HTTPException, Request
from app.models import SignupRequest, LoginRequest
from app.auth import sign_up, authenticate
from app.db import execute

router = APIRouter()


@router.post("/signup")
def signup(req: SignupRequest):
    try:
        sub = sign_up(req.email, req.password, artist_name=req.artist_name, artist_type=req.artist_type, genre=req.genre)
    except Exception as e:
        msg = str(e)
        if "UsernameExists" in msg:
            raise HTTPException(409, "Email already registered")
        raise HTTPException(400, msg)
    execute(
        "INSERT INTO workspace_users (cognito_sub,username,email,first_name,last_name,artist_name,artist_type,genre) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (sub, req.username, req.email, req.first_name, req.last_name, req.artist_name, req.artist_type, req.genre),
    )
    return {"status": "ok", "user_sub": sub}


@router.post("/login")
async def login(request: Request):
    body = await request.json()
    try:
        return authenticate(body["email"], body["password"])
    except Exception:
        raise HTTPException(401, "Invalid credentials")
