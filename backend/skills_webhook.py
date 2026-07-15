"""Webhook handler — receives skill data, generates PDF, saves to S3, returns URL."""
import json, uuid, boto3
from io import BytesIO

# Optional: install reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

s3 = boto3.client("s3")
BUCKET = "artispreneur-outputs"


def generate_epk_pdf(artist_data: dict) -> bytes:
    """Generate EPK PDF from artist profile data."""
    if not HAS_REPORTLAB:
        return _simple_text_pdf(artist_data, "EPK")
    
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.79, 0.64, 0.15)  # gold
    c.drawString(50, 750, "Artispreneur")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, 735, "Electronic Press Kit")
    
    name = artist_data.get("stage_name") or artist_data.get("name", "Artist")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawString(50, 700, name)
    
    y = 670
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    for label, key in [("Genre:", "genre"), ("Location:", "current_city"), ("Years Active:", "years"), ("PRO:", "pro")]:
        val = artist_data.get(key, "")
        if val:
            c.drawString(50, y, f"{label} {val}")
            y -= 16
    
    y -= 10
    c.drawString(50, y, "Bio:")
    bio = artist_data.get("story") or artist_data.get("bio", "Artist bio coming soon.")
    for line in bio.split("\n")[:8]:
        y -= 14
        c.drawString(60, y, line[:90])
    
    c.save()
    buf.seek(0)
    return buf.read()


def _simple_text_pdf(data: dict, doc_type: str) -> bytes:
    """Fallback: plain text PDF."""
    buf = BytesIO()
    text = json.dumps(data, indent=2)
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Courier", 10)
    y = 750
    for line in text.split("\n"):
        c.drawString(40, y, line[:100])
        y -= 12
        if y < 50: break
    c.save()
    buf.seek(0)
    return buf.read()


def handler(event, context):
    """AWS Lambda handler for POST /v1/skills/generate."""
    try:
        body = json.loads(event.get("body", "{}"))
        skill_type = body.get("skill_type", "epk")
        artist_data = body.get("artist_data", {})
        username = artist_data.get("stage_name", "artist").lower().replace(" ", "-")
        
        pdf_bytes = generate_epk_pdf(artist_data)
        
        key = f"users/{username}/outputs/{skill_type}/{uuid.uuid4()}.pdf"
        s3.put_object(Bucket=BUCKET, Key=key, Body=pdf_bytes, ContentType="application/pdf")
        
        url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=3600)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "ok", "url": url, "s3_key": key}),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
