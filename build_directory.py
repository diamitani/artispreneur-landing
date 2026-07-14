import re, json

with open("/Users/patmini/Desktop/Master Artispreneur/knowledge-base/sites/directory-data.ts") as f:
    raw = f.read()

# Extract categories with their sections and entries
categories = []
# Pattern: each top-level object in the categories array
cat_pattern = re.compile(
    r'{\s*\n\s*id:\s*"(\w+)"\s*,\s*title:\s*"([^"]+)"\s*,\s*slug:\s*"(\w+)"[^}]*?sections:\s*\[(.*?)\]\s*\n\s*\}',
    re.DOTALL
)

all_contacts = []
for match in cat_pattern.finditer(raw):
    cat_id, cat_title, cat_slug, sections_raw = match.groups()
    
    # Extract sections from this category
    sec_pattern = re.compile(
        r'{\s*\n\s*title:\s*"([^"]+)"\s*,\s*slug:\s*"(\w+)"[^}]*?entries:\s*\[(.*?)\]\s*\n\s*\}',
        re.DOTALL
    )
    
    for sec_match in sec_pattern.finditer(sections_raw):
        sec_title, sec_slug, entries_raw = sec_match.groups()
        
        # Extract individual entries
        entry_pattern = re.compile(
            r'{\s*name:\s*"([^"]+)"\s*(?:,\s*location:\s*"([^"]*)")?\s*(?:,\s*url:\s*"([^"]*)")?\s*(?:,\s*tags:\s*\[(.*?)\])?\s*(?:,\s*genre:\s*"([^"]*)")?\s*(?:,\s*notes:\s*"([^"]*)")?\s*}',
            re.DOTALL
        )
        
        for ent_match in entry_pattern.finditer(entries_raw):
            name = ent_match.group(1)
            location = ent_match.group(2) or ""
            url = ent_match.group(3) or ""
            tags_str = ent_match.group(4) or ""
            genre = ent_match.group(5) or ""
            notes = ent_match.group(6) or ""
            
            # Parse tags
            tags = []
            if tags_str:
                tags = [t.strip().strip('"\'') for t in tags_str.split(',') if t.strip().strip('"\'')]
            
            all_contacts.append({
                "name": name,
                "location": location,
                "url": url,
                "tags": tags,
                "genre": genre,
                "notes": notes,
                "cat": cat_title,
                "section": sec_title
            })

print(f"Extracted {len(all_contacts)} contacts in {len(categories)} categories")

# Write JS file
js = "const DIRECTORY_DATA = " + json.dumps(all_contacts, indent=2) + ";"
with open("/tmp/artispreneur-landing/directory-data.js", "w") as f:
    f.write(js)

size = len(js)
print(f"Wrote directory-data.js ({size:,} bytes)")
