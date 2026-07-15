"""
Artispreneur Backend — AWS Lambda (FastAPI + Mangum)
Auth: Cognito | LLM: Bedrock DeepSeek V3 | DB: RDS PostgreSQL
"""
import json, os, uuid, boto3
from datetime import datetime, timezone
from mangum import Mangum
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2, psycopg2.extras

app = FastAPI(title="Artispreneur API", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

bedrock = boto3.client("bedrock-runtime")
s3 = boto3.client("s3")
cognito = boto3.client("cognito-idp")
BEDROCK_MODEL = os.environ.get("BEDROCK_MODEL", "deepseek.deepseek-v3")
S3_OUTPUTS = os.environ["S3_OUTPUTS"]
COGNITO_CLIENT = os.environ["COGNITO_CLIENT"]

def get_db():
    return psycopg2.connect(host=os.environ["DB_HOST"], dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"])

def get_user(request: Request) -> str:
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "): raise HTTPException(401)
    try:
        return cognito.get_user(AccessToken=auth.split(" ")[1])["Username"]
    except: raise HTTPException(401)

class ChatReq(BaseModel):
    message: str; agent_type: str = "manager"

class SignupReq(BaseModel):
    email: str; password: str; username: str
    first_name: str = ""; last_name: str = ""
    artist_name: str = ""; artist_type: str = ""; genre: str = ""

AGENT_PROMPTS = {
    "pro": "PRO Agent — help artists register with BMI/ASCAP/SESAC, register songs, track royalties, create splitsheets.",
    "distribution": "Distribution Agent — help with DSP accounts, playlist strategy, ad spend, release planning.",
    "licensing": "Licensing Agent — find sync opportunities, create pitches, submit to music libraries.",
    "legal": "Legal Agent — LLC formation, EIN registration, contracts, operating agreements.",
    "finance": "Finance Agent — business banking, tax management, transaction analysis.",
    "manager": "Manager Agent — business plans, calendar, projects, content, research. Route to specialists when needed.",
}

@app.post("/auth/signup")
def signup(req: SignupReq):
    try:
        resp = cognito.sign_up(ClientId=COGNITO_CLIENT, Username=req.email, Password=req.password,
            UserAttributes=[{"Name":"email","Value":req.email},{"Name":"custom:artist_name","Value":req.artist_name}])
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO workspace_users (cognito_sub,username,email,first_name,last_name,artist_name,artist_type,genre) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (resp["UserSub"], req.username, req.email, req.first_name, req.last_name, req.artist_name, req.artist_type, req.genre))
        db.commit(); cur.close(); db.close()
        return {"status":"ok","user_sub":resp["UserSub"]}
    except cognito.exceptions.UsernameExistsException: raise HTTPException(409,"Email registered")
    except Exception as e: raise HTTPException(400,str(e))

@app.post("/auth/login")
async def login(request: Request):
    body = await request.json()
    try:
        resp = cognito.initiate_auth(ClientId=COGNITO_CLIENT, AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME":body["email"],"PASSWORD":body["password"]})
        return {"access_token":resp["AuthenticationResult"]["AccessToken"],"id_token":resp["AuthenticationResult"]["IdToken"]}
    except: raise HTTPException(401,"Invalid credentials")

@app.post("/agent/chat")
async def chat(req: ChatReq, user: str = Depends(get_user)):
    system = AGENT_PROMPTS.get(req.agent_type, AGENT_PROMPTS["manager"])
    try:
        resp = bedrock.invoke_model(modelId=BEDROCK_MODEL, body=json.dumps({
            "messages":[{"role":"system","content":system},{"role":"user","content":req.message}],
            "temperature":0.7,"max_tokens":2048}))
        reply = json.loads(resp["body"].read())["choices"][0]["message"]["content"]
        return {"reply":reply,"agent_type":req.agent_type}
    except Exception as e: raise HTTPException(500,f"Bedrock: {str(e)}")

@app.get("/agent/status")
def status(user: str = Depends(get_user)):
    db = get_db(); cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT agent_type,status FROM agent_sessions WHERE user_id=(SELECT id FROM workspace_users WHERE cognito_sub=%s)",(user,))
    return {"agents":[dict(r) for r in cur.fetchall()]}

@app.get("/directory")
def directory(category: str = None, search: str = None):
    db = get_db(); cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    q = "SELECT * FROM contacts"; params = []
    if category: q += " WHERE category=%s"; params.append(category)
    if search:
        w = "WHERE" if "WHERE" not in q else "AND"
        q += f" {w} (name ILIKE %s OR location ILIKE %s)"; s=f"%{search}%"; params.extend([s,s])
    q += " ORDER BY name LIMIT 100"
    cur.execute(q,params)
    return {"contacts":[dict(r) for r in cur.fetchall()]}

@app.get("/health")
def health(): return {"status":"ok","model":BEDROCK_MODEL,"timestamp":datetime.now(timezone.utc).isoformat()}

handler = Mangum(app)
