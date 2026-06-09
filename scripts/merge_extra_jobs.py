#!/usr/bin/env python3
"""merge_extra_jobs.py — Merge JobStreet/Indeed jobs from Windows CDP scraper
Enriches with AI-searchable fields and filters to chef/kitchen/culinary roles only.

Usage:
  1. Chrome 开 remote debugging port 9222
  2. Run: node scrape_extra_jobs.js (Windows Desktop)
  3. Run: python3 scripts/merge_extra_jobs.py (WSL, from jbkitchen root)
"""
import json, sys, os, re

# Import enrichment from scrape_jobs
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from scrape_jobs import _enrich_job, _classify_category, JOB_KEYWORDS

# Use CloakBrowser-scraped output (WSL path, no Windows dependency)
EXTRAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "extra_jobs_output.json")
JOBS_FILE = os.path.join(os.path.dirname(__file__), "..", "site", "data", "jobs.json")
JOBS_FILE2 = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")

# KITCHEN KEYWORDS — only keep jobs a chef/kitchen worker would apply for
KITCHEN_TITLE_PATTERNS = re.compile(
    r'\b(chef|cook|kitchen|commis|demi|sous|pastry|baker|culinary|'
    r'tukang.masak|pembantu.dapur|line.cook|grill|wok|kitchen.helper|'
    r'kitchen.crew|food.service|restaurant|catering|steward|dishwasher|'
    r'baking|barista|butcher|prep.cook|food.prep|production.cook|'
    r'hotel.cook|banquet|kitchen.hand)\b',
    re.IGNORECASE
)

# Keywords that disqualify a title (non-kitchen roles)
EXCLUDE_PATTERNS = re.compile(
    r'\b(admin|administrator|manager|supervisor|executive|director|'
    r'technologist|specialist|analyst|consultant|auditor|engineer|'
    r'sales|marketing|finance|account|hr|human.resource|logistic|'
    r'purchasing|buyer|clerk|driver|cleaner|guard|security|receptionist|'
    r'graphic.designer|it.support)\b',
    re.IGNORECASE
)


def is_kitchen_role(job):
    """Filter: only keep jobs a chef/kitchen worker would apply for"""
    title = job.get("title", "") or ""
    company = job.get("company", "") or ""
    combined = f"{title} {company}"

    # Exclude non-kitchen roles first
    if EXCLUDE_PATTERNS.search(title):
        return False

    # Must match kitchen keywords
    return bool(KITCHEN_TITLE_PATTERNS.search(combined))


def salary_text_to_struct(raw):
    """Convert raw salary string like 'RM 3,000 - RM 5,000 per month' to structured"""
    if not raw:
        return {"min": None, "max": None, "period": "monthly", "text": None}
    raw = str(raw).strip()
    text = raw
    m = re.search(r'([\d,]+)\s*[-–]\s*([\d,]+)', raw.replace(',', ''))
    if m:
        period = "monthly"
        if re.search(r'per\s*(year|annum|annual|yr)', raw, re.IGNORECASE):
            period = "yearly"
        return {
            "min": int(m.group(1).replace(',', '')),
            "max": int(m.group(2).replace(',', '')),
            "period": period,
            "text": text
        }
    m = re.search(r'([\d,]+)', raw.replace(',', ''))
    if m:
        return {"min": int(m.group(1).replace(',', '')), "max": int(m.group(1).replace(',', '')), "period": "monthly", "text": text}
    return {"min": None, "max": None, "period": "monthly", "text": text if text else None}


if not os.path.exists(EXTRAS_FILE):
    print(f"❌ Extras not found: {EXTRAS_FILE}")
    print("   Run node scrape_extra_jobs.js from Windows first (Chrome CDP required).")
    sys.exit(1)

with open(EXTRAS_FILE) as f:
    extras = json.load(f)

extra_items = extras.get("items", [])
print(f"📥 Raw extras: {len(extra_items)}")

# Convert salary strings to struct, then enrich & filter
converted = []
for j in extra_items:
    # Convert salary
    if isinstance(j.get("salary"), str):
        j["salary"] = salary_text_to_struct(j["salary"])
    elif j.get("salary") is None:
        j["salary"] = {"min": None, "max": None, "period": "monthly", "text": None}

    # Enrich (add category, skills, etc)
    try:
        j = _enrich_job(j)
    except Exception as e:
        j["category"] = "other"
        j["id"] = f"js-{hash(j.get('title','')+j.get('company',''))%1000000:06x}"

    converted.append(j)

# Filter to kitchen roles only
filtered = [j for j in converted if is_kitchen_role(j)]
print(f"📊 After enrichment: {len(converted)} → kitchen roles: {len(filtered)}")

# Source breakdown
by_source = {}
for j in filtered:
    s = j.get("source", "?")
    by_source[s] = by_source.get(s, 0) + 1
for s, n in sorted(by_source.items()):
    print(f"  {s}: {n}")

# Show first few examples
for j in filtered[:5]:
    print(f"  [{j.get('category','?')}] {j.get('title','')[:55]} — {j.get('company','')[:20]}")

# Merge into existing data
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
    for j in filtered:
        key = f"{j.get('title','')}|{j.get('company','')}"
        if key not in existing_ids:
            merged.append(j)
            existing_ids.add(key)
            added += 1

    data["items"] = merged
    data["count"] = len(merged)
    if "by_source" not in data:
        data["by_source"] = {}
    for s, n in by_source.items():
        data["by_source"][s] = data["by_source"].get(s, 0) + n

    with open(target, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n  {target}: {len(existing)} → {len(merged)} (+{added})")

print(f"\n✅ 合并完成。Run 'cd site && hugo --minify && touch ../docs/.nojekyll && cd .. && git add -A && git commit -m \"extra jobs\" && git push' to deploy.")
