#!/usr/bin/env python3
"""update_fb_cookies.py — Read Windows-extracted FB cookies and inject into fb_job_scraper.js

Usage:
  1. User opens Chrome with --remote-debugging-port=9222 and logs into Facebook
  2. User runs: node jbkitchen_fb_cookies.js (from Windows Desktop)
  3. Then run:  python3 scripts/update_fb_cookies.py  (from jbkitchen root)
"""
import json, re, sys, os

COOKIE_FILE = "/mnt/c/Users/User/Desktop/fb-cookie-extract/cookies_output.json"
SCRAPER_FILE = os.path.join(os.path.dirname(__file__), "fb_job_scraper.js")

if not os.path.exists(COOKIE_FILE):
    print(f"❌ Cookie file not found: {COOKIE_FILE}")
    print("   Run node jbkitchen_fb_cookies.js from Windows first.")
    sys.exit(1)

with open(COOKIE_FILE) as f:
    data = json.load(f)

needed = ['c_user', 'xs', 'fr', 'presence']
for key in ['c_user', 'xs']:
    if not data.get(key):
        print(f"❌ Missing {key} in cookie file")
        sys.exit(1)

with open(SCRAPER_FILE) as f:
    content = f.read()

# Replace each cookie value in the COOKIES array
for key in needed:
    old_val = data.get(key, '')
    if not old_val:
        continue
    # Match: { name: 'key', value: '...', ... }
    pattern = rf"(name:\s*'{key}'\s*,\s*value:\s*)'[^']*'"
    replacement = rf"\1'{old_val}'"
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        print(f"  ✅ Updated {key}")
        content = new_content
    else:
        print(f"  ⚠️  Could not find {key} in scraper (may need to add it)")

with open(SCRAPER_FILE, 'w') as f:
    f.write(content)

print(f"\n✅ Cookies updated in: {SCRAPER_FILE}")
print("   Run 'bash jbkitchen-full-pipeline.sh' to test the scraper.")
