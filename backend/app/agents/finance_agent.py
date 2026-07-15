"""Finance Agent — banking, taxes, transaction analysis, quarterly estimates."""
from app.agents.framework import BaseAgent, Tool, registry

class FinanceAgent(BaseAgent):
    agent_type="finance"; icon="$"; color="#06b6d2"
    def __init__(self):
        self.tools=[
            Tool("revenue_analysis","Analyze streaming and performance revenue",self._revenue,{}),
            Tool("estimate_taxes","Calculate quarterly estimated tax payment",self._taxes,{"quarterly_income":"number"}),
            Tool("track_expenses","Log and categorize a business expense",self._expense,{"amount":"number","category":"string","description":"string?"}),
            Tool("financial_summary","Get YTD financial summary",self._summary,{}),
            Tool("deduction_checklist","List music business tax deductions",self._deductions,{}),
        ]
    def system_prompt(self,**kw):return"You are the Finance Agent. Help with revenue analysis, tax estimates, expense tracking, and financial planning. Be clear and accurate — money matters are serious."
    def _revenue(self):return {"total_ytd":4230.00,"breakdown":{"streaming":2140.00,"shows":1200.00,"sync":500.00,"merch":390.00},"quarterly_trend":"up 15%"}
    def _taxes(self,quarterly_income:float):return {"estimated_tax":round(quarterly_income*0.30,2),"federal":round(quarterly_income*0.22,2),"self_employment":round(quarterly_income*0.153,2),"state":round(quarterly_income*0.05,2),"due_date":"Oct 15, 2026"}
    def _expense(self,amount:float,category:str,description:str=""):return {"logged":True,"amount":amount,"category":category,"deductible":category in ["equipment","travel","marketing","studio","home_office","education"]}
    def _summary(self):return {"ytd_revenue":4230.00,"ytd_expenses":1240.00,"net":2990.00,"largest_expense_category":"equipment","months_remaining_in_year":5}
    def _deductions(self):return {"deductions":["Home studio/office (sq ft)","Equipment & instruments","Travel & mileage","Marketing & promotion","Professional services (legal, accounting)","Education & training","Software subscriptions","Internet & phone (business %)"]}
registry.add(FinanceAgent())
