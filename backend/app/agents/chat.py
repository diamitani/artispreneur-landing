"""Agent chat — Bedrock + registry routing + tool execution."""
from app.agents.framework import registry
from app.agents.pro_agent import PROAgent
from app.agents.distribution_agent import DistributionAgent
from app.agents.licensing_agent import LicensingAgent
from app.agents.legal_agent import LegalAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.manager_agent import ManagerAgent
from app.config import config
import json, boto3

_bedrock = boto3.client("bedrock-runtime")

# Ensure all agents registered
assert len(registry.agents) == 6, f"Expected 6 agents, got {len(registry.agents)}"


def chat(message: str, agent_type: str = "manager", context: dict | None = None) -> dict:
    """Route message to agent, optionally execute tools, return response."""
    # Route intent if using manager
    if agent_type == "manager":
        routed = registry.route(message)
        if routed != "manager":
            agent_type = routed
    
    agent = registry.get(agent_type)
    if not agent:
        agent = registry.get("manager")
    
    system = agent.system_prompt(**(context or {}))
    tools_schema = agent.tool_schema()
    
    # Call Bedrock with tool definitions
    try:
        resp = _bedrock.invoke_model(
            modelId=config.bedrock_model,
            body=json.dumps({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                "tools": json.loads(tools_schema) if agent.tools else [],
                "temperature": 0.7,
                "max_tokens": 2048,
            }),
        )
        result = json.loads(resp["body"].read())
        reply = result["choices"][0]["message"]["content"]
    except Exception:
        reply = f"Manager Agent here. Let me route that to the right specialist. What specific area do you need help with? I have agents for: PRO/royalties, distribution/playlists, licensing/sync, legal/contracts, and finance/taxes."

    return {
        "reply": reply,
        "agent_type": agent_type,
        "agent_icon": agent.icon,
        "agent_color": agent.color,
    }


def execute_tool(agent_type: str, tool_name: str, **params) -> dict:
    """Execute a specific tool on an agent."""
    agent = registry.get(agent_type)
    if not agent:
        return {"ok": False, "error": f"Agent '{agent_type}' not found"}
    return agent.execute(tool_name, **params)


def get_agents_status() -> list[dict]:
    """Return all registered agents with metadata."""
    return [{
        "type": a.agent_type,
        "icon": a.icon,
        "color": a.color,
        "tools_count": len(a.tools),
    } for a in registry.agents.values()]
