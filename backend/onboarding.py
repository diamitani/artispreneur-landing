"""
Onboarding service — S3 provisioning, link scraping, PAL bio generation.
Works standalone or as Lambda handler.
"""
import json, os, re, uuid, boto3
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from dataclasses import dataclass, field, asdict


@dataclass
class ArtistProfile:
    name: str = ""
    stage_name: str = ""
    hometown: str = ""
    current_city: str = ""
    genre: str = ""
    years: str = ""
    employment: str = ""
    budget: str = ""
    living: str = ""
    gear: str = ""
    why_music: str = ""
    influences: str = ""
    story: str = ""
    message: str = ""
    experience: list = field(default_factory=list)
    show_count: str = ""
    press: str = ""
    goals: list = field(default_factory=list)
    links: dict = field(default_factory=dict)
    scraped_data: dict = field(default_factory=dict)
    profile_image: str = ""


class S3Provisioner:
    """Creates per-user S3 bucket structure."""
    
    def __init__(self, bucket: str = "artispreneur-outputs"):
        self.s3 = boto3.client("s3")
        self.bucket = bucket
    
    def provision(self, username: str) -> str:
        prefix = f"users/{username}/"
        folders = [
            prefix,
            f"{prefix}.rostr/state/",
            f"{prefix}outputs/contracts/",
            f"{prefix}outputs/epks/",
            f"{prefix}outputs/analysis/",
            f"{prefix}catalog/",
            f"{prefix}profile/",
        ]
        for folder in folders:
            self.s3.put_object(Bucket=self.bucket, Key=folder)
        return f"s3://{self.bucket}/{prefix}"


class LinkScraper:
    """Scrapes metadata from artist music/press links."""
    
    SPOTIFY_REGEX = re.compile(r'spotify\.com/artist/(\w+)')
    YOUTUBE_REGEX = re.compile(r'youtube\.com/(@|channel/)([\w-]+)')
    INSTAGRAM_REGEX = re.compile(r'instagram\.com/([\w.]+)')
    
    def scrape(self, links: dict) -> dict:
        results = {}
        for platform, url in links.items():
            if not url: continue
            handler = getattr(self, f"_scrape_{platform}", None)
            if handler:
                try: results[platform] = handler(url)
                except Exception as e: results[platform] = {"error": str(e)}
            else:
                results[platform] = {"url": url, "platform": platform}
        return results
    
    def _scrape_spotify(self, url: str) -> dict:
        match = self.SPOTIFY_REGEX.search(url)
        return {"artist_id": match.group(1) if match else "", "platform": "spotify", "url": url}
    
    def _scrape_youtube(self, url: str) -> dict:
        match = self.YOUTUBE_REGEX.search(url)
        return {"channel": match.group(0) if match else "", "platform": "youtube", "url": url}
    
    def _scrape_instagram(self, url: str) -> dict:
        match = self.INSTAGRAM_REGEX.search(url)
        return {"handle": match.group(1) if match else "", "platform": "instagram", "url": url}


class PALBioGenerator:
    """Generates professional artist bio from profile data using PAL compilation."""
    
    TEMPLATES = {
        "emerging": "{name} is an emerging {genre} artist {location}making waves with their {adjective} sound. {story_short}",
        "established": "{name} is a {genre} artist {location}with {years} of experience. {story_short}",
        "veteran": "With {years} in the game, {name} has established themselves as a force in {genre}. {story_short}",
    }
    
    def generate(self, profile: ArtistProfile) -> str:
        name = profile.stage_name or profile.name or "The Artist"
        genre = profile.genre or "music"
        location = f"out of {profile.current_city or profile.hometown} " if profile.hometown else ""
        story = profile.story or profile.why_music or ""
        story_short = story[:200] + "..." if len(story) > 200 else story
        influences = profile.influences.split(",")[:3] if profile.influences else []
        experience = profile.experience
        years = profile.years or ""
        goals = profile.goals
        
        # Pick template based on years
        if "10+" in years or "5-10" in years: template = self.TEMPLATES["veteran"]
        elif "3-5" in years: template = self.TEMPLATES["established"]
        else: template = self.TEMPLATES["emerging"]
        
        adjective = self._adjective_from_genre(genre)
        
        bio = template.format(name=name, genre=genre, location=location, story_short=story_short, years=years, adjective=adjective)
        
        if influences:
            bio += f"\n\nDrawing from influences like {', '.join(influences)}, {name.split()[0]} creates music that {profile.message or 'resonates deeply'}."
        
        if experience:
            bio += f"\n\n{name.split()[0]} has {', '.join(experience[:3]).lower()}."
        
        if goals:
            bio += f"\n\nCurrently focused on {', '.join(goals[:3]).lower()}."
        
        return bio
    
    def _adjective_from_genre(self, genre: str) -> str:
        mapping = {"hip-hop":"raw","r&b":"soulful","electronic":"immersive","rock":"powerful","jazz":"sophisticated","pop":"captivating","latin":"fiery","afrobeats":"rhythmic"}
        return mapping.get(genre.lower().split("/")[0].strip(), "distinctive")


class KnowledgeBaseBuilder:
    """Compiles onboarding data into master knowledge base + soul.md."""
    
    def build(self, profile: ArtistProfile, scraped: dict) -> dict:
        kb = {
            "version": "1.0",
            "artist": asdict(profile),
            "scraped_data": scraped,
            "soul_md": self._build_soul(profile, scraped),
            "bio": PALBioGenerator().generate(profile),
        }
        return kb
    
    def _build_soul(self, profile: ArtistProfile, scraped: dict) -> str:
        p = profile
        lines = [
            f"# Artist: {p.stage_name or p.name}",
            f"# Hometown: {p.hometown}",
            f"# Current City: {p.current_city}",
            f"# Genre: {p.genre}",
            f"# Years in Music: {p.years}",
            f"# Employment: {p.employment}",
            f"# Budget: {p.budget}",
            f"# Why Music: {p.why_music}",
            f"# Message: {p.message}",
            f"# Goals: {', '.join(p.goals)}",
        ]
        if scraped:
            for platform, data in scraped.items():
                lines.append(f"# {platform.title()}: {json.dumps(data)}")
        return "\n".join(lines)


def process_onboarding(onboarding_data: dict) -> dict:
    """Full onboarding pipeline — provision, scrape, build, return."""
    profile = ArtistProfile(**{k: v for k, v in onboarding_data.items() if k in ArtistProfile.__dataclass_fields__})
    
    # 1. Provision S3
    username = (profile.stage_name or profile.name or "artist").lower().replace(" ", "-")
    s3_path = S3Provisioner().provision(username)
    
    # 2. Scrape links
    scraped = LinkScraper().scrape(profile.links)
    
    # 3. Build knowledge base
    kb = KnowledgeBaseBuilder().build(profile, scraped)
    
    # 4. Save to S3
    s3 = boto3.client("s3")
    bucket = "artispreneur-outputs"
    s3.put_object(Bucket=bucket, Key=f"users/{username}/.rostr/soul.md", Body=kb["soul_md"])
    s3.put_object(Bucket=bucket, Key=f"users/{username}/knowledge-base/profile.json", Body=json.dumps(kb))
    
    return {"status": "ok", "s3_path": s3_path, "knowledge_base": kb}


# Lambda handler
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    result = process_onboarding(body)
    return {"statusCode": 200, "body": json.dumps(result)}
