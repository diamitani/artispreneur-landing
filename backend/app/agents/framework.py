"""
Agent framework — base class, tool registry, intent routing.
All 6 agents inherit from BaseAgent and register tools.
"""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable
    parameters: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """Every Artispreneur agent inherits from this."""
    
    agent_type: str
    icon: str
    color: str
    tools: list[Tool] = []
    
    @abstractmethod
    def system_prompt(self, **context) -> str:
        """Return the system prompt with optional user context."""
        ...
    
    def register(self, tool: Tool):
        self.tools.append(tool)
    
    def execute(self, tool_name: str, **params) -> dict:
        """Execute a registered tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    return {"ok": True, "result": tool.handler(**params)}
                except Exception as e:
                    return {"ok": False, "error": str(e)}
        return {"ok": False, "error": f"Tool '{tool_name}' not found"}
    
    def tool_schema(self) -> str:
        """JSON schema of all tools for LLM function calling."""
        return json.dumps([{
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
        } for t in self.tools])


class AgentRegistry:
    """Holds all agents, routes intents to the right one."""
    
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
    
    def add(self, agent: BaseAgent):
        self.agents[agent.agent_type] = agent
    
    def get(self, agent_type: str) -> BaseAgent | None:
        return self.agents.get(agent_type)
    
    def route(self, message: str) -> str:
        """Simple keyword routing — production uses Bedrock for NLU."""
        m = message.lower()
        if any(w in m for w in ['pro','bmi','ascap','sesac','royalty','register','splitsheet','isrc','catalog']):
            return 'pro'
        if any(w in m for w in ['distribute','playlist','spotify','apple music','dsp','stream','release','ads']):
            return 'distribution'
        if any(w in m for w in ['license','sync','tv','film','commercial','library','supervisor','pitch']):
            return 'licensing'
        if any(w in m for w in ['llc','ein','contract','legal','incorporate','agreement','trademark','operating']):
            return 'legal'
        if any(w in m for w in ['tax','finance','bank','revenue','money','budget','expense','quarterly','deduction']):
            return 'finance'
        return 'manager'
    
    def all_agents(self) -> list[dict]:
        return [{"type": a.agent_type, "icon": a.icon, "color": a.color} for a in self.agents.values()]


# Singleton
registry = AgentRegistry()
