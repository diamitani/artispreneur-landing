"""Bedrock DeepSeek V3 agent chat."""
import json, boto3
from app.config import config

_bedrock = boto3.client("bedrock-runtime")

PROMPTS = {
    "pro": "PRO Agent — help artists register with BMI/ASCAP/SESAC, register songs, track royalties, create splitsheets.",
    "distribution": "Distribution Agent — DSP accounts, playlist strategy, ad spend, release planning.",
    "licensing": "Licensing Agent — sync opportunities, pitch templates, music library submissions.",
    "legal": "Legal Agent — LLC formation, EIN registration, contracts, operating agreements.",
    "finance": "Finance Agent — business banking, tax management, transaction analysis.",
    "manager": "Manager Agent — business plans, calendar, projects, content. Route to specialists.",
}


def chat(message: str, agent_type: str = "manager") -> str:
    """Send message to Bedrock DeepSeek V3, return reply."""
    system = PROMPTS.get(agent_type, PROMPTS["manager"])
    resp = _bedrock.invoke_model(
        modelId=config.bedrock_model,
        body=json.dumps({
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }),
    )
    return json.loads(resp["body"].read())["choices"][0]["message"]["content"]
