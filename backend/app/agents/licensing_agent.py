"""Licensing Agent — sync licensing, music libraries, supervisor pitches."""
from app.agents.framework import BaseAgent, Tool, registry

class LicensingAgent(BaseAgent):
    agent_type="licensing"; icon="⚡"; color="#a855f7"
    def __init__(self):
        self.tools=[
            Tool("find_sync_ops","Find sync licensing opportunities",self._find_sync,{"genre":"string","type":"string?"}),
            Tool("create_pitch","Create a tailored pitch for a music supervisor",self._create_pitch,{"track":"string","supervisor":"string","context":"string?"}),
            Tool("submit_to_library","Submit music to a sync library",self._submit_library,{"track":"string","library":"string"}),
            Tool("list_libraries","List music libraries accepting submissions",self._list_libraries,{}),
        ]
    def system_prompt(self,ctx=None):return"You are the Licensing Agent. Find sync opportunities, create pitch templates, submit to music libraries. Be proactive and specific."
    def _find_sync(self,genre:str,typ:str=""):return{"opportunities":[{"show":"Netflix Drama S3","type":"TV","genre":genre,"deadline":"2026-08-15"},{"film":"Indie Feature","type":"Film","genre":genre,"budget":"$500-2000/song"},{"brand":"Tech Commercial","type":"Ad","genre":"upbeat "+genre,"budget":"$2000-5000"}]}
    def _create_pitch(self,track:str,supervisor:str,ctx=""):return{"pitch":f"Hi {supervisor},\\n\\nI think '{track}' would be a great fit for your project. {ctx}\\n\\nLink: streaming.link/{track}\\n\\nThanks for listening!"}
    def _submit_library(self,track:str,library:str):return{"status":"submitted","track":track,"library":library}
    def _list_libraries(self):return{"libraries":["Musicbed","Artlist","Pond5","AudioJungle","Epidemic Sound","Music Vine"]}
registry.add(LicensingAgent())
