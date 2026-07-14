"""Agent: Parse courses.ts and generate individual course detail HTML pages."""
import re, os, html as h

SRC = "/Users/patmini/Desktop/Master Artispreneur/knowledge-base/sites/academy/lib/courses.ts"
OUT = "/tmp/artispreneur-landing/courses"

with open(SRC) as f:
    raw = f.read()

# Extract courseDescriptions dict first
desc_map = {}
desc_block = re.search(r'courseDescriptions:.*?\n\}', raw, re.DOTALL)
if desc_block:
    pairs = re.findall(r'"([^"]+)":\s*\{[^}]*description:\s*"([^"]*(?:[^"\\]|\\.)*)"', desc_block.group(0), re.DOTALL)
    for title, desc in pairs:
        desc_map[title] = desc

# Find all top-level courses
# Each course starts with: { id: "N", title: "...", slug: "...", category: "...", ... modules: [...] }
courses_raw = re.findall(
    r'\{[^{]*?id:\s*"(\d+)".*?title:\s*"([^"]+)".*?slug:\s*"([^"]+)".*?category:\s*"([^"]+)".*?modules:\s*\[(.*?)\],\s*\n\s*\}',
    raw, re.DOTALL
)

print(f"Found {len(courses_raw)} courses")

os.makedirs(OUT, exist_ok=True)
course_slugs = []

for cid, title, slug, category, modules_raw in courses_raw:
    desc = desc_map.get(title, f"Learn {title.lower()} in this Artispreneur Academy course.")
    
    # Extract modules
    modules = re.findall(
        r'id:\s*"([^"]+)".*?number:\s*"([^"]+)".*?title:\s*"([^"]+)".*?chapterTitle:\s*"([^"]+)".*?content:\s*`([^`]*)`.*?duration:\s*"([^"]+)".*?videoUrl:\s*"([^"]+)"',
        modules_raw, re.DOTALL
    )
    
    if not modules:
        # Try alternate pattern
        modules = re.findall(
            r'id:\s*"([^"]+)".*?number:\s*"([^"]+)".*?title:\s*"([^"]+)".*?chapterTitle:\s*"([^"]+)".*?content:\s*`([^`]*)`',
            modules_raw, re.DOTALL
        )
    
    course_slugs.append(slug)
    
    # Build module HTML
    mod_html = ""
    for i, mod in enumerate(modules):
        mid, num, mtitle, ctitle, content = mod[0], mod[1], mod[2], mod[3], mod[4]
        dur = mod[5] if len(mod) > 5 else "8 min"
        vid = mod[6] if len(mod) > 6 else ""
        
        # Clean content
        content = h.escape(content).replace('\n', '<br>')
        
        mod_html += f'''
        <div class="module">
          <div class="module-header">
            <span class="module-num">Module {num}</span>
            <h3>{h.escape(mtitle)}</h3>
            <span class="module-dur">{dur}</span>
          </div>
          <p class="module-chapter">{h.escape(ctitle)}</p>
          <div class="module-content">{content}</div>
        </div>'''
    
    # Build full page
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{h.escape(title)} — Artispreneur Academy</title>
<meta name="description" content="{h.escape(desc[:160])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<style>
:root{{--black:#09090b;--black-light:#111113;--surface:#18181b;--card:#1c1c1f;--border:#27272a;--border-light:#3f3f46;--text:#fafafa;--text-muted:#a1a1aa;--text-dim:#71717a;--gold:#c9a227;--gold-light:#e8c84a;--gold-muted:rgba(201,162,39,0.12);--max-w:800px}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{-webkit-font-smoothing:antialiased}}
body{{font-family:'Inter',-apple-system,sans-serif;background:var(--black);color:var(--text);line-height:1.7}}
a{{color:var(--gold);text-decoration:none;transition:color .2s}}
a:hover{{color:var(--gold-light)}}
.container{{max-width:var(--max-w);margin:0 auto;padding:0 24px}}
.navbar{{position:fixed;top:0;left:0;right:0;z-index:1000;padding:0 24px;background:rgba(9,9,11,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
.navbar-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px}}
.nav-links{{display:flex;align-items:center;gap:24px}}
.nav-links a{{color:var(--text-muted);font-size:13px;font-weight:500;white-space:nowrap}}
.nav-links a:hover{{color:var(--text)}}
main{{padding-top:100px;padding-bottom:80px}}
.breadcrumb{{font-size:13px;color:var(--text-dim);margin-bottom:24px}}
.breadcrumb a{{color:var(--text-dim)}}
.breadcrumb a:hover{{color:var(--gold)}}
.course-title{{font-family:'Playfair Display',serif;font-size:clamp(28px,3.5vw,42px);font-weight:900;margin-bottom:8px}}
.course-meta{{display:flex;gap:16px;margin-bottom:8px;font-size:13px}}
.course-cat{{padding:3px 10px;border-radius:100px;font-size:11px;font-weight:600;background:var(--gold-muted);color:var(--gold)}}
.course-lessons{{color:var(--text-dim)}}
.course-desc{{font-size:15px;color:var(--text-muted);margin-bottom:40px;line-height:1.7;max-width:650px}}
.module{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:28px;margin-bottom:20px;transition:all .2s}}
.module:hover{{border-color:var(--border-light)}}
.module-header{{display:flex;align-items:center;gap:14px;margin-bottom:6px}}
.module-num{{font-size:11px;font-weight:700;color:var(--gold);background:var(--gold-muted);padding:3px 10px;border-radius:4px;white-space:nowrap}}
.module-header h3{{font-size:17px;font-weight:700;flex:1}}
.module-dur{{font-size:11px;color:var(--text-dim);white-space:nowrap}}
.module-chapter{{font-size:12px;color:var(--text-dim);margin-bottom:14px;text-transform:uppercase;letter-spacing:.5px}}
.module-content{{font-size:14px;color:var(--text-muted);line-height:1.8}}
.module-content br{{display:block;content:'';margin-bottom:8px}}
.cta{{text-align:center;margin-top:48px;padding:36px;background:var(--surface);border:1px solid var(--border);border-radius:16px}}
.cta h2{{font-size:20px;font-weight:700;margin-bottom:8px}}
.cta p{{font-size:14px;color:var(--text-muted);margin-bottom:16px}}
.cta .btn{{display:inline-block;background:var(--gold);color:var(--black);padding:12px 28px;border-radius:8px;font-weight:700;font-size:14px;transition:all .2s}}
.cta .btn:hover{{background:var(--gold-light)}}
footer{{background:var(--card);border-top:1px solid var(--border);padding:32px 0;text-align:center;font-size:13px;color:var(--text-dim)}}
@media(max-width:640px){{.module-header{{flex-wrap:wrap}}.nav-links{{display:none}}}}
</style>
</head>
<body>
<nav class="navbar">
  <div class="navbar-inner">
    <a href="../index.html"><img src="../logo.png" alt="Artispreneur" style="height:24px;display:block"></a>
    <div class="nav-links">
      <a href="../index.html#agents">Agents</a>
      <a href="../academy.html">Academy</a>
      <a href="../directory.html">Directory</a>
      <a href="../pricing.html">Pricing</a>
      <a href="../about.html">About</a>
    </div>
  </div>
</nav>

<main class="container">
  <p class="breadcrumb"><a href="../index.html">Home</a> / <a href="../academy.html">Academy</a> / {h.escape(title)}</p>
  <h1 class="course-title">{h.escape(title)}</h1>
  <div class="course-meta">
    <span class="course-cat">{h.escape(category)}</span>
    <span class="course-lessons">{len(modules)} lessons</span>
  </div>
  <p class="course-desc">{h.escape(desc)}</p>
  {mod_html}
  <div class="cta">
    <h2>Want more?</h2>
    <p>Get the full experience with video lessons on the Artispreneur Academy.</p>
    <a href="https://academy-build.vercel.app/#courses" class="btn">Open Full Academy →</a>
  </div>
</main>
<footer><p>© 2026 Artispreneur · Art Means Business</p></footer>
</body>
</html>'''
    
    fpath = os.path.join(OUT, f"{slug}.html")
    with open(fpath, 'w') as f:
        f.write(html)
    print(f"  ✓ {slug}.html ({len(modules)} modules)")

print(f"\nGenerated {len(course_slugs)} course pages in {OUT}/")
