#!/usr/bin/env python3
"""update_fb_cookies.py — Read Windows-extracted FB cookies and save to fb_cookies.json

Usage:
  1. User opens Chrome with --remote-debugging-port=9222 and logs into Facebook
  2. User runs: node jbkitchen_fb_cookies.js (from Windows Desktop)
  3. Then run:  python3 scripts/update_fb_cookies.py  (from jbkitchen root)
"""
import json, sys, os

COOKIE_FILE = "/mnt/c/Users/User/Desktop/fb-cookie-extract/cookies_output.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "fb_cookies.json")

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

# Build the JSON for fb_cookies.json
cookies = {k: data.get(k, '') for k in needed}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(cookies, f, indent=2)

print(f"✅ Cookies saved to: {OUTPUT_FILE}")
print(f"   (fb_cookies.json is gitignored — safe from commits)")
print(f"   c_user: {cookies['c_user']}")
print(f"   xs: {cookies['xs'][:20]}...")
print("\nNext cron run will pick up the new cookies automatically.")
