"""PRO Agent — BMI/ASCAP/SESAC registration, royalties, splitsheets, catalog."""
import json
from app.agents.framework import BaseAgent, Tool, registry


class PROAgent(BaseAgent):
    agent_type = "pro"
    icon = "♩"
    color = "#c9a227"
    
    def __init__(self):
        self.tools = [
            Tool("register_song", "Register a song with a PRO (BMI/ASCAP/SESAC)", self._register_song, {
                "title": "string", "isrc": "string?", "cowriters": "list?", "splits": "object?"
            }),
            Tool("create_splitsheet", "Generate a splitsheet document for collaborators", self._create_splitsheet, {
                "track_title": "string", "collaborators": "list", "percentages": "object"
            }),
            Tool("check_registration_status", "Check if a song is registered with your PRO", self._check_status, {
                "title": "string", "isrc": "string?"
            }),
            Tool("list_catalog", "List all registered songs in your catalog", self._list_catalog, {}),
            Tool("extract_metadata", "Extract metadata from a song file or link", self._extract_metadata, {
                "source": "string"
            }),
        ]
    
    def system_prompt(self, context: dict | None = None) -> str:
        ctx = ""
        if context:
            ctx = f"\nArtist: {context.get('artist_name','')}\nPRO: {context.get('pro','')}\nCatalog: {context.get('catalog_count',0)} works"
        return f"""You are the PRO Agent for Artispreneur. Help artists register with BMI, ASCAP, or SESAC, register songs, track royalties, and create splitsheets.
{ctx}
Always be concise. When an artist asks to register a song, ask for: title, co-writers with split percentages, and ISRC if available."""
    
    def _register_song(self, title: str, isrc: str = "", cowriters: list = None, splits: dict = None) -> dict:
        return {"status": "registered", "title": title, "isrc": isrc or f"US-{title[:3].upper()}-{hash(title)%100000:05d}", "cowriters": cowriters or [], "splits": splits or {}}
    
    def _create_splitsheet(self, track_title: str, collaborators: list, percentages: dict) -> dict:
        return {"document": f"{track_title}_splitsheet.pdf", "collaborators": collaborators, "percentages": percentages, "total": sum(percentages.values())}
    
    def _check_status(self, title: str, isrc: str = "") -> dict:
        return {"title": title, "registered": True, "pro": "BMI", "registration_date": "2026-06-15"}
    
    def _list_catalog(self) -> dict:
        return {"works": 14, "songs": ["Gold Hour", "Midnight in the Garden", "Blue", "Fade"], "total_royalties_ytd": 1240.00}
    
    def _extract_metadata(self, source: str) -> dict:
        return {"title": "Extracted Track", "bpm": 120, "key": "Am", "duration": "3:45", "isrc": "US-XYZ-12-34567"}


registry.add(PROAgent())
