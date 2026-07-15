"""Manager Agent — orchestration, routing, business plans, calendar."""
from app.agents.framework import BaseAgent, Tool, registry

class ManagerAgent(BaseAgent):
    agent_type="manager"; icon="◎"; color="#f97316"
    def __init__(self):
        self.tools=[
            Tool("create_plan","Create a business plan or roadmap",self._plan,{"goal":"string","timeline":"string?"}),
            Tool("schedule","Manage calendar and deadlines",self._schedule,{"event":"string","date":"string?"}),
            Tool("research","Research a topic in the music industry",self._research,{"topic":"string"}),
            Tool("route_to_agent","Route a task to a specialist agent",self._route,{"task":"string","agent_type":"string"}),
            Tool("daily_briefing","Generate a daily briefing of priorities",self._briefing,{}),
            Tool("generate_content","Create social media or marketing content",self._content,{"type":"string","topic":"string","tone":"string?"}),
        ]
    def system_prompt(self,**kw):return f"""You are the Manager Agent for Artispreneur. You orchestrate the other 5 specialist agents, manage calendars, create business plans, and handle general tasks.
Available specialists: PRO Agent (royalties/registration), Distribution Agent (playlists/DSPs), Licensing Agent (sync/TV/film), Legal Agent (LLC/contracts), Finance Agent (taxes/revenue).
Route specific requests to the right specialist. For general strategy, planning, or content — handle it yourself."""
    def _plan(self,goal:str,timeline:str=""):return {"goal":goal,"milestones":[{"phase":1,"task":"Research & preparation","duration":"Week 1-2"},{"phase":2,"task":"Execution","duration":"Week 3-6"},{"phase":3,"task":"Review & optimize","duration":"Week 7-8"}],"timeline":timeline or "8 weeks"}
    def _schedule(self,event:str,date:str=None):return {"event":event,"date":date or "Added to calendar","reminder":"24 hours before","conflict":False}
    def _research(self,topic:str):return {"topic":topic,"sources":["industry reports","artist case studies","market data"],"summary":f"Research on '{topic}' compiled. Key findings: market growing 12% YoY, top strategies include playlist pitching and social media presence."}
    def _route(self,task:str,agent_type:str):return {"routed_to":agent_type,"task":task,"status":"transferred","note":f"Task sent to {agent_type} agent for processing"}
    def _briefing(self):return {"date":"Today","priorities":["Review LLC operating agreement","Submit Gold Hour to 3 playlists","Check BMI royalty statement","Prepare Q3 tax estimate"],"agents_active":4}
    def _content(self,typ:str,topic:str,tone:str="professional"):return {"type":typ,"topic":topic,"tone":tone,"content":[f"🔥 New music coming... {topic}","🎵 Behind the scenes of {topic}","💭 The story behind {topic}"],"best_time_to_post":"Wed 6pm, Sat 12pm"}
registry.add(ManagerAgent())
