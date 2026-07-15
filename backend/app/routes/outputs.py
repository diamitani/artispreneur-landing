"""GET /outputs, POST /outputs"""
import uuid, boto3
from fastapi import APIRouter, Depends, Request, HTTPException
from app.auth import get_user
from app.config import config
from app.db import fetch_all, execute

router = APIRouter()
_s3 = boto3.client("s3")


@router.get("")
def list_outputs(user: str = Depends(get_user)):
    return {"outputs": fetch_all(
        "SELECT id, type, title, s3_key, status, created_at FROM outputs WHERE user_id=(SELECT id FROM workspace_users WHERE cognito_sub=%s) ORDER BY created_at DESC",
        (user,),
    )}


@router.post("")
async def upload_output(request: Request, user: str = Depends(get_user)):
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(400, "No file provided")
    output_type = form.get("type", "other")
    title = form.get("title", file.filename or "untitled")
    s3_key = f"users/{user}/outputs/{output_type}/{uuid.uuid4()}-{file.filename}"
    _s3.upload_fileobj(file.file, config.s3_outputs, s3_key)
    execute(
        "INSERT INTO outputs (user_id, type, title, s3_key) VALUES ((SELECT id FROM workspace_users WHERE cognito_sub=%s),%s,%s,%s)",
        (user, output_type, title, s3_key),
    )
    return {"s3_key": s3_key}
