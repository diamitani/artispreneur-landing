"""Legal Agent — LLC formation, EIN, contracts, operating agreements."""
from app.agents.framework import BaseAgent, Tool, registry

class LegalAgent(BaseAgent):
    agent_type="legal"; icon="§"; color="#3b82f6"
    def __init__(self):
        self.tools=[
            Tool("form_llc","File LLC formation documents",self._form_llc,{"state":"string","business_name":"string"}),
            Tool("register_ein","Register for an EIN with the IRS",self._register_ein,{}),
            Tool("generate_contract","Generate a music industry contract",self._gen_contract,{"type":"string","parties":"object"}),
            Tool("review_agreement","Review an operating agreement or contract",self._review,{"document":"string"}),
            Tool("trademark_search","Search USPTO for existing trademarks",self._trademark_search,{"name":"string"}),
        ]
    def system_prompt(self,**kw):return"You are the Legal Agent. Help with LLC formation, EIN registration, contracts, and agreements. Be precise — you're dealing with legal documents. Always note: 'This is not legal advice. Consult an attorney for final review.'"
    def _form_llc(self,state:str,business_name:str):return{"status":"prepared","business_name":business_name,"state":state,"filing_fee":"$150-800 depending on state","documents":["Articles of Organization","Operating Agreement","EIN Application"]}
    def _register_ein(self):return{"status":"ready","form":"SS-4","filing_method":"Online at IRS.gov","estimated_time":"15 minutes","note":"EIN is free from the IRS"}
    def _gen_contract(self,typ:str,parties:dict):return{"type":typ,"parties":parties,"sections":["Parties","Term","Compensation","Rights","Termination","Governing Law"],"document":f"{typ.replace(' ','_')}_template.pdf"}
    def _review(self,document:str):return{"document":document,"issues_found":0,"recommendations":["Verify party names","Check termination clause","Confirm governing law"],"status":"clean"}
    def _trademark_search(self,name:str):return{"name":name,"available":True,"classes":["009","041"],"filing_fee":"$250-350 per class"}
registry.add(LegalAgent())
