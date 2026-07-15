"""Cognito authentication helpers."""
import boto3
from fastapi import Request, HTTPException
from app.config import config

_cognito = boto3.client("cognito-idp")


def get_user(request: Request) -> str:
    """Extract Cognito sub from Authorization Bearer token."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    try:
        return _cognito.get_user(AccessToken=auth.split(" ")[1])["Username"]
    except Exception:
        raise HTTPException(401, "Invalid token")


def sign_up(email: str, password: str, **attrs) -> str:
    """Register user in Cognito. Returns UserSub."""
    user_attrs = [{"Name": "email", "Value": email}]
    for key, val in attrs.items():
        if val:
            user_attrs.append({"Name": f"custom:{key}", "Value": val})
    return _cognito.sign_up(
        ClientId=config.cognito_client,
        Username=email, Password=password,
        UserAttributes=user_attrs,
    )["UserSub"]


def authenticate(email: str, password: str) -> dict:
    """Login — returns tokens."""
    resp = _cognito.initiate_auth(
        ClientId=config.cognito_client,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": password},
    )
    auth = resp["AuthenticationResult"]
    return {"access_token": auth["AccessToken"], "id_token": auth["IdToken"]}
