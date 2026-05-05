import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v22.0")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
LIMIT = int(os.getenv("INSTAGRAM_LIMIT", "12"))
OUTPUT = os.getenv("INSTAGRAM_OUTPUT", "instagram-feed.json")

if not ACCESS_TOKEN or not IG_USER_ID:
    print("ERRO: configure os secrets INSTAGRAM_ACCESS_TOKEN e IG_USER_ID no GitHub.", file=sys.stderr)
    sys.exit(1)

fields = "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username"
params = urllib.parse.urlencode({
    "fields": fields,
    "limit": LIMIT,
    "access_token": ACCESS_TOKEN,
})
url = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_USER_ID}/media?{params}"

with urllib.request.urlopen(url, timeout=30) as response:
    payload = json.loads(response.read().decode("utf-8"))

items = []
for item in payload.get("data", []):
    media_type = item.get("media_type", "")
    media_url = item.get("media_url") or item.get("thumbnail_url")
    thumb = item.get("thumbnail_url") or media_url
    if not media_url and not thumb:
        continue
    items.append({
        "id": item.get("id"),
        "caption": item.get("caption", ""),
        "media_type": media_type,
        "media_url": media_url,
        "thumbnail_url": thumb,
        "permalink": item.get("permalink"),
        "timestamp": item.get("timestamp"),
        "username": item.get("username", "selectuniformes"),
    })

out = {
    "profile": "selectuniformes",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "items": items,
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Feed gerado com {len(items)} itens em {OUTPUT}")
