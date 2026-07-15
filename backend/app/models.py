"""Pydantic request/response models."""
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str
    username: str
    first_name: str = ""
    last_name: str = ""
    artist_name: str = ""
    artist_type: str = ""
    genre: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "manager"


class TokenResponse(BaseModel):
    access_token: str
    id_token: str
