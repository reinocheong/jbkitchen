#!/usr/bin/env python3
"""scrape_jobstreet_wsl.py — Scrape JobStreet JB kitchen jobs via CloakBrowser (stealth)
Replaces Windows Chrome CDP scraper. Uses CloakBrowser's anti-bot Chromium.

Output: data/extra_jobs_output.json (project root)
"""

import json, os, time, sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(PROJECT_DIR, "data", "extra_jobs_output.json")

# CloakBrowser stealth Chromium
CLOAK_CHROMIUM = "/home/user/.cloakbrowser/chromium-146.0.7680.177.5/chrome"

KEYWORDS = [
    'chef', 'cook', 'kitchen', 'commis', 'demi-chef',
    'sous-chef', 'pastry', 'baker', 'culinary', 'kitchen-hand',
    'tukang-masak', 'catering', 'line-cook'
]

BASE_URL = "https://my.jobstreet.com/{kw}-jobs/in-Johor-Bahru"

LAUNCH_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-setuid-sandbox',
    '--window-size=1280,900',
]


def scrape_jobstreet():
    from playwright.sync_api import sync_playwright

    all_jobs = []
    seen = set()

    with sync_playwright() as p:
        # Launch CloakBrowser (stealth, passes Cloudflare)
        browser = p.chromium.launch(
            headless=True,
            executable_path=CLOAK_CHROMIUM,
            args=LAUNCH_ARGS
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-MY",
        )
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            // Override chrome.runtime to look like a real browser
            window.chrome = { runtime: {} };
        """)

        page = ctx.new_page()

        for kw in KEYWORDS:
            url = BASE_URL.format(kw=kw)
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                # Wait for job cards to appear (Cloudflare should be bypassed by Cloak)
                try:
                    page.wait_for_selector('[data-automation*="normalJob"]', timeout=15000)
                except Exception:
                    pass  # might be empty results page

                time.sleep(2)

                # Scroll to trigger lazy load
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)

                jobs = page.evaluate("""() => {
                    const cards = document.querySelectorAll('[data-automation*=normalJob]');
                    return Array.from(cards).map(card => {
                        const titleEl = card.querySelector('[data-automation*=jobTitle]');
                        const companyEl = card.querySelector('[data-automation*=jobCompany]');
                        const locEl = card.querySelector('[data-automation*=jobLocation], [data-automation*=jobCardLocation]');
                        const salaryEl = card.querySelector('[data-automation*=jobSalary]');
                        const dateEl = card.querySelector('[data-automation*=jobListingDate]');
                        const descEl = card.querySelector('[data-automation*=jobShortDescription]');
                        return {
                            title: titleEl?.textContent?.trim() || '',
                            company: companyEl?.textContent?.trim() || '',
                            location: locEl?.textContent?.trim() || 'Johor Bahru',
                            salary: salaryEl?.textContent?.trim()?.replace(/\\s+/g, ' ') || null,
                            description: descEl?.textContent?.trim()?.substring(0, 300) || null,
                            date: dateEl?.textContent?.trim() || '',
                            source: 'JobStreet'
                        };
                    }).filter(j => j.title && j.title.length > 3);
                }""")

                new_jobs = []
                for j in jobs:
                    key = j['title'] + '|' + j['company']
                    if key not in seen:
                        seen.add(key)
                        new_jobs.append(j)
                all_jobs.extend(new_jobs)
                print(f"  {kw}: {len(jobs)} found, {len(new_jobs)} new")
            except Exception as e:
                print(f"  {kw}: {str(e)[:80]}")

        browser.close()

    output = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(all_jobs),
        "by_source": {"JobStreet": len(all_jobs)},
        "items": all_jobs
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Total: {len(all_jobs)} jobs saved to {OUTPUT}")
    return all_jobs


if __name__ == '__main__':
    scrape_jobstreet()
