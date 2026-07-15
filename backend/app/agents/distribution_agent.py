"""Distribution Agent — DSP management, playlists, ad campaigns."""
from app.agents.framework import BaseAgent, Tool, registry


class DistributionAgent(BaseAgent):
    agent_type = "distribution"
    icon = "↗"
    color = "#22c55e"
    
    def __init__(self):
        self.tools = [
            Tool("find_playlists", "Find genre-matched Spotify playlists for submission", self._find_playlists, {"genre": "string"}),
            Tool("submit_to_playlist", "Submit a track to a specific playlist", self._submit_playlist, {"track": "string", "playlist": "string"}),
            Tool("streaming_stats", "Get streaming stats across all DSPs", self._stats, {}),
            Tool("create_ad_campaign", "Create a social media ad campaign for a release", self._create_ad, {"track": "string", "budget": "number", "platform": "string"}),
            Tool("compare_dsps", "Compare distribution platforms (UnitedMasters, DistroKid, CD Baby, TuneCore)", self._compare_dsps, {}),
        ]
    
    def system_prompt(self, context: dict | None = None) -> str:
        return f"""You are the Distribution Agent for Artispreneur. Help artists manage DSP accounts, find playlists, run ad campaigns, and plan releases.
Be strategic. Suggest specific playlists and platforms based on the artist's genre: {context.get('genre','') if context else ''}."""
    
    def _find_playlists(self, genre: str) -> dict:
        return {"playlists": [
            {"name": f"{genre} Rising", "followers": 12000, "curator": "IndieCurator"},
            {"name": f"Fresh {genre}", "followers": 8500, "curator": "FreshFinds"},
            {"name": f"Late Night Vibes", "followers": 15000, "curator": "MoodMusic"},
        ]}
    
    def _submit_playlist(self, track: str, playlist: str) -> dict:
        return {"status": "submitted", "track": track, "playlist": playlist, "estimated_review": "3-5 days"}
    
    def _stats(self) -> dict:
        return {"spotify": {"streams": 12400, "listeners": 3200}, "apple_music": {"streams": 5800, "listeners": 1400}, "youtube": {"views": 2100}}
    
    def _create_ad(self, track: str, budget: float, platform: str) -> dict:
        return {"campaign_id": f"ad_{hash(track)%10000}", "track": track, "budget": budget, "platform": platform, "estimated_reach": int(budget * 100)}
    
    def _compare_dsps(self) -> dict:
        return {"platforms": [
            {"name": "UnitedMasters", "fee": "Free tier + $59.99/yr Premium", "royalty_split": "100%", "best_for": "Independence + brand deals"},
            {"name": "DistroKid", "fee": "$22.99/yr unlimited", "royalty_split": "100%", "best_for": "High-volume releases"},
            {"name": "CD Baby", "fee": "$9.95/single, $29/album (one-time)", "royalty_split": "91%", "best_for": "One-time fee, no annual"},
            {"name": "TuneCore", "fee": "$14.99/single, $29.99/album per year", "royalty_split": "100%", "best_for": "Publishing admin included"},
        ]}


registry.add(DistributionAgent())
