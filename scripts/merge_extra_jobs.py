#!/usr/bin/env python3
"""merge_extra_jobs.py — Merge JobStreet/Indeed jobs from Windows CDP scraper

Usage:
  1. Chrome 开 remote debugging port 9222
  2. Run: node scrape_jobstreet_indeed.js (Windows Desktop)
  3. Run: python3 scripts/merge_extra_jobs.py (WSL, from jbkitchen root)
"""
import json, sys, os

EXTRAS_FILE = "/mnt/c/Users/User/Desktop/fb-cookie-extract/extra_jobs_output.json"
JOBS_FILE = os.path.join(os.path.dirname(__file__), "..", "site", "data", "jobs.json")
JOBS_FILE2 = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")

if not os.path.exists(EXTRAS_FILE):
    print(f"❌ Extras not found: {EXTRAS_FILE}")
    print("   Run node scrape_jobstreet_indeed.js from Windows first (Chrome CDP required).")
    sys.exit(1)

with open(EXTRAS_FILE) as f:
    extras = json.load(f)

extra_items = extras.get("items", [])
print(f"📥 Extra jobs: {len(extra_items)} (JobStreet={extras.get('by_source',{}).get('JobStreet',0)}, Indeed={extras.get('by_source',{}).get('Indeed',0)})")

for target in [JOBS_FILE, JOBS_FILE2]:
    with open(target) as f:
        data = json.load(f)

    existing = data.get("items", [])
    existing_ids = set()
    for j in existing:
        key = f"{j.get('title','')}|{j.get('company','')}"
        existing_ids.add(key)

    merged = list(existing)
    added = 0
    for j in extra_items:
        key = f"{j.get('title','')}|{j.get('company','')}"
        if key not in existing_ids:
            merged.append(j)
            existing_ids.add(key)
            added += 1

    data["items"] = merged
    data["count"] = len(merged)
    if "by_source" not in data:
        data["by_source"] = {}
    data["by_source"]["JobStreet"] = extras.get("by_source", {}).get("JobStreet", 0)
    data["by_source"]["Indeed"] = extras.get("by_source", {}).get("Indeed", 0)

    with open(target, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  {target}: {len(existing)} → {len(merged)} (+{added})")

print(f"\n✅ 合并完成。Run 'cd site && hugo --minify && touch ../docs/.nojekyll && cd .. && git add -A && git commit -m \"extra jobs\" && git push' to deploy.")
