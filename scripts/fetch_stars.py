#!/usr/bin/env python3
"""
获取新账号已 star 的仓库列表
运行一次，保存到 starred_repos.json
"""
import urllib.request
import json
import time

# ============ 配置区 ============
TOKEN    = "ghp_新账号TOKEN"
USERNAME = "TreasureBoy99"
OUT_FILE = "/root/github-migration/data/starred_repos.json"
# ===============================

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

all_stars = []
page = 1

print(f"Fetching stars for {USERNAME}...", flush=True)
while True:
    url = f"https://api.github.com/users/{USERNAME}/starred?per_page=100&page={page}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Page {page} error: {e}", flush=True)
        break

    if not data:
        break

    for r in data:
        all_stars.append({
            "full_name": r["full_name"],
            "html_url": r["html_url"],
            "updated_at": r.get("updated_at", "")
        })

    print(f"Page {page}: +{len(data)} (total: {len(all_stars)})", flush=True)

    if len(data) < 100:
        break

    page += 1
    time.sleep(1)

with open(OUT_FILE, 'w') as f:
    json.dump(all_stars, f, ensure_ascii=False)
print(f"\nDone! Saved {len(all_stars)} stars to {OUT_FILE}", flush=True)
