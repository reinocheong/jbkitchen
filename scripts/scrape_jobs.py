#!/usr/bin/env python3
"""
jbkitchen — JB 餐饮招聘数据聚合器
从 Jora、Hiredly、Maukerja 抓取 JB 厨师/餐饮职位
输出 site/data/jobs.json（Hugo 数据源）
"""
import os, re, json, time, math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urljoin
import hashlib

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", ".logs")
MYT = ZoneInfo("Asia/Kuala_Lumpur")
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept-Language": "en-MY,en;q=0.9,ms;q=0.8,zh-CN;q=0.7,zh;q=0.6",
})
JOB_KEYWORDS = [
    "chef", "cook", "kitchen", "commis", "demi", "sous chef",
    "head chef", "pastry", "baker", "culinary", "kitchen helper",
    "tukang masak", "pembantu dapur", "catering", "food service",
    "restaurant", "kitchen crew", "line cook",
]


def _log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "scrape_jobs.log"), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def _normalise_date(raw: str) -> str:
    """Convert various date formats to ISO date string YYYY-MM-DD"""
    raw = (raw or "").strip().lower()
    if not raw:
        return datetime.now(MYT).strftime("%Y-%m-%d")

    # ISO date already embedded
    m = re.search(r'(\d{4}-\d{2}-\d{2})', raw)
    if m:
        return m.group(1)

    now = datetime.now(MYT)

    # "2 days ago", "16 days ago"
    m = re.search(r'(\d+)\s*days?\s*ago', raw)
    if m:
        return (now - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")

    # "a month ago", "a day ago"
    if 'month' in raw:
        return (now - timedelta(days=30)).strftime("%Y-%m-%d")
    if 'day' in raw or 'hour' in raw or 'min' in raw:
        return now.strftime("%Y-%m-%d")

    # "Posted 2d ago" etc
    m = re.search(r'(\d+)\s*(d|day|h|hr|min)\s*ago', raw)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit in ('d', 'day'):
            delta = timedelta(days=n)
        elif unit in ('h', 'hr'):
            delta = timedelta(hours=n)
        else:
            delta = timedelta(minutes=n)
        return (now - delta).strftime("%Y-%m-%d")

    return now.strftime("%Y-%m-%d")


def _parse_salary(text) -> dict:
    """Parse salary string into structured format"""
    if not text:
        return {"min": None, "max": None, "period": "monthly", "text": None}
    text = str(text).strip()
    text = re.sub(r'^(rm|rm\s+|salary\s*:?\s*|月薪\s*:?\s*)', '', text, flags=re.IGNORECASE).strip()
    orig = text

    # "5,000 - 7,000 per month"
    m = re.search(r'([\d,]+)\s*-\s*([\d,]+)', text.replace(',', ''))
    if m:
        period = "monthly"
        if re.search(r'per\s*(year|annum|annual|yr)', text, re.IGNORECASE):
            period = "yearly"
        return {
            "min": int(m.group(1).replace(',', '')),
            "max": int(m.group(2).replace(',', '')),
            "period": period,
            "text": orig,
        }

    m = re.search(r'([\d,]+)', text.replace(',', ''))
    if m:
        val = int(m.group(1).replace(',', ''))
        return {"min": val, "max": val, "period": "monthly", "text": orig}

    return {"min": None, "max": None, "period": "monthly", "text": orig if orig else None}


def _dedup_jobs(jobs: list) -> list:
    """Deduplicate by title+company combo"""
    seen = set()
    result = []
    for j in jobs:
        key = (j.get("title", "").lower().strip(), j.get("company", "").lower().strip())
        if key in seen:
            continue
        seen.add(key)
        result.append(j)
    return result


# ── Enrichment: AI-searchable fields ────────────────────────────────────

SKILL_PATTERNS = [
    (r'\b(Pastry|Baking|Baker)\b', ["Pastry", "Baking"]),
    (r'\b(Chinese Cuisine|Chinese Cooking|Dim Sum|Dimsum)\b', ["Chinese Cuisine", "Dim Sum"]),
    (r'\b(Western Cuisine|Western Cooking|Western Food)\b', ["Western Cuisine"]),
    (r'\b(Japanese Cuisine|Sushi|Ramen|Teppanyaki|Japanese)\b', ["Japanese Cuisine"]),
    (r'\b(Korean Cuisine|Korean BBQ|Korean)\b', ["Korean Cuisine"]),
    (r'\b(Malay Cuisine|Malay Cooking|Roti Canai|Nasi Lemak)\b', ["Malay Cuisine"]),
    (r'\b(Indian Cuisine|Roti|Naan|Tandoori|Banana Leaf)\b', ["Indian Cuisine"]),
    (r'\b(Italian|Pizza|Pasta)\b', ["Italian Cuisine"]),
    (r'\b(Grill|BBQ|Barbecue)\b', ["Grill"]),
    (r'\b(Seafood|Fish)\b', ["Seafood"]),
    (r'\b(Butcher|Butchery|Meat Preparation)\b', ["Butchery"]),
    (r'\b(Food Safety|HACCP|Hygiene)\b', ["Food Safety"]),
    (r'\b(Halal)\b', ["Halal"]),
    (r'\b(Catering|Banquet)\b', ["Catering"]),
    (r'\b(Barista|Coffee|Beverage)\b', ["Barista"]),
    (r'\b(Noodle|Mee|Mie)\b', ["Noodles"]),
    (r'\b(Menu Planning|Menu Development)\b', ["Menu Planning"]),
    (r'\b(Cost Control|Inventory|Stock)\b', ["Cost Control", "Inventory"]),
    (r'\b(Team Lead|Supervisor|Management)\b', ["Team Leading"]),
    (r'\b(Deep Fry|Wok|Stir Fry)\b', ["Wok Cooking"]),
]

KNOWN_JB_AREAS = [
    "Mount Austin", "EduCity", "Iskandar Puteri", "Tebrau", "Skudai",
    "Kulai", "Pasir Gudang", "Johor Jaya", "Desa Tebrau", "Molek",
    "Permas Jaya", "Bukit Indah", "Nusa Bestari", "Sutera", "Senai",
    "Ulu Tiram", "Masai", "Gelang Patah", "Kota Tinggi", "Pontian",
    "Taman Daya", "Setia Tropika", "Johor Bahru",
]

CATEGORY_RULES = [
    (r'\b(Head Chef|Executive Chef|Sous Chef|Demi Chef|Chef de Partie|Pastry Chef|Master Chef)\b', "chef"),
    (r'\b(Chef\b)', "chef"),
    (r'\b(Cook|Tukang Masak|Pembantu Dapur|Line Cook|Commis|Kitchen Crew)\b', "cook"),
    (r'\b(Kitchen Helper|Kitchen Assistant|Steward|Dishwasher)\b', "kitchen-crew"),
    (r'\b(Waiter|Waitress|Barista|Service Crew|Captain|Pelayan|F&B Service|FB Service)\b', "fb-service"),
    (r'\b(Manager|Supervisor|Ops Lead|Restaurant Manager|F&B Manager|FB Manager|Outlet Manager)\b', "management"),
]


def _generate_id(title: str, company: str, source: str) -> str:
    """Generate sha256 ID from title+company+source"""
    raw = f"{title.lower()}|{company.lower()}|{source.lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _normalize_title(title: str) -> str:
    """Clean title: remove ALL CAPS, standardize common titles"""
    if not title:
        return ""
    t = title.strip()

    # Detect ALL CAPS (>=50% uppercase alpha chars)
    alpha_chars = [c for c in t if c.isalpha()]
    if alpha_chars and sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars) >= 0.5:
        t = t.title()

    # Standardize common titles
    replacements = {
        "Tukang Masak": "Tukang Masak",
        "Pembantu Dapur": "Pembantu Dapur",
        "Chef De Partie": "Chef de Partie",
        "Sous Chef": "Sous Chef",
        "Demi Chef": "Demi Chef",
        "Head Chef": "Head Chef",
        "Pastry Chef": "Pastry Chef",
        "Commis Chef": "Commis Chef",
        "Line Cook": "Line Cook",
        "Kitchen Crew": "Kitchen Crew",
        "Kitchen Helper": "Kitchen Helper",
        "Restaurant Manager": "Restaurant Manager",
        "Outlet Manager": "Outlet Manager",
        "F&B Manager": "F&B Manager",
        "Service Crew": "Service Crew",
        "Barista": "Barista",
    }
    for pattern, standard in replacements.items():
        if pattern.lower() in t.lower():
            t = re.sub(re.escape(pattern), standard, t, flags=re.IGNORECASE)
            break

    return t


def _classify_category(title: str) -> str:
    """Classify job into: chef, cook, kitchen-crew, fb-service, management, other"""
    if not title:
        return "other"
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, title, re.IGNORECASE):
            return category
    return "other"


def _detect_employment_type(title: str, salary_text: str = None) -> str | None:
    """Detect employment type: full-time, part-time, contract, or None"""
    combined = f"{title or ''} {salary_text or ''}"
    cl = combined.lower()
    if re.search(r'\bfull[- ]?time\b', cl) or 'sepenuh masa' in cl:
        return "full-time"
    if re.search(r'\bpart[- ]?time\b', cl) or 'separuh masa' in cl:
        return "part-time"
    if re.search(r'\bcontract\b|kontrak', cl):
        return "contract"
    return None


def _normalize_location(location: str) -> str:
    """Extract city area from location string"""
    if not location:
        return "Johor Bahru"
    loc = location.strip()
    for area in KNOWN_JB_AREAS:
        if area.lower() in loc.lower():
            return area
    # Fallback: return cleaned version
    loc = re.sub(r',\s*Johor\s*$', '', loc, flags=re.IGNORECASE).strip()
    loc = re.sub(r',\s*Malaysia\s*$', '', loc, flags=re.IGNORECASE).strip()
    return loc if loc else "Johor Bahru"


def _detect_skills(title: str, salary_text: str = None, description: str = "") -> list:
    """Detect skills from title and text content"""
    combined = f"{title or ''} {salary_text or ''} {description or ''}"
    skills = set()
    for pattern, labels in SKILL_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            for label in labels:
                skills.add(label)
    return sorted(skills)


def _format_salary_text(salary: dict) -> str | None:
    """Create human-readable salary string like 'RM3,000 - RM5,000/month'"""
    if not salary:
        return None
    mn = salary.get("min")
    mx = salary.get("max")
    period = salary.get("period", "monthly")
    period_label = {"monthly": "/month", "yearly": "/year", "hourly": "/hour"}.get(period, "/month")

    if mn is not None and mx is not None:
        if mn == mx:
            return f"RM{mn:,.0f}{period_label}"
        return f"RM{mn:,.0f} - RM{mx:,.0f}{period_label}"
    elif mn is not None:
        return f"RM{mn:,.0f}{period_label}"
    return None


def _enrich_job(job: dict) -> dict:
    """Add AI-searchable fields to a job item (modifies in place, returns for chaining)"""
    title = job.get("title", "")
    company = job.get("company", "")
    source = job.get("source", "")
    salary = job.get("salary", {})
    location = job.get("location", "")
    salary_text = salary.get("text") if salary else None

    job["id"] = _generate_id(title, company, source)
    job["title_normalized"] = _normalize_title(title)
    job["category"] = _classify_category(title)
    job["employment_type"] = _detect_employment_type(title, salary_text)
    job["location_normalized"] = _normalize_location(location)
    job["skills"] = _detect_skills(title, salary_text)
    job["description"] = None  # Not available from listings; may be enriched later
    if salary:
        formatted = _format_salary_text(salary)
        if formatted:
            salary["text_formatted"] = formatted

    return job


# ── Jora (requests + BS4) ──────────────────────────────────────────────

def scrape_jora(max_pages=4) -> list:
    """Scrape Jora Malaysia for chef/cook jobs in Johor Bahru"""
    jobs = []
    base_url = "https://my.jora.com/Chef-jobs-in-Johor-Bahru-Johor"

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        try:
            resp = SESSION.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            _log(f"Jora page {page} 失败: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.job-card.result")
        if not cards:
            break

        for card in cards:
            title_el = card.select_one("h2.job-title a.job-link")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = urljoin("https://my.jora.com", title_el.get("href", ""))

            company_el = card.select_one("span.job-company")
            company = company_el.get_text(strip=True) if company_el else ""

            location_el = card.select_one("a.job-location")
            location = location_el.get_text(strip=True) if location_el else "Johor Bahru"

            date_el = card.select_one("span.job-listed-date")
            date_raw = date_el.get_text(strip=True) if date_el else ""

            salary_text = None
            for b in card.select("div.badges div.badge.-default-badge div.content"):
                txt = b.get_text(strip=True)
                if "RM" in txt:
                    salary_text = txt
                    break

            jobs.append({
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "salary": _parse_salary(salary_text),
                "date": _normalise_date(date_raw),
                "url": link,
                "source": "Jora",
            })

        time.sleep(1)

    _log(f"Jora: {len(jobs)} 条")
    return jobs


# ── Hiredly (requests + __NEXT_DATA__) ────────────────────────────────

def scrape_hiredly() -> list:
    """Scrape Hiredly F&B jobs in Johor via __NEXT_DATA__"""
    jobs = []
    urls = [
        "https://my.hiredly.com/jobs-in-food-beverage/in-johor",
        "https://my.hiredly.com/jobs-in-food-beverage/food-beverage-on-ground/in-johor",
    ]

    for url in urls:
        try:
            resp = SESSION.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            _log(f"Hiredly {url} 失败: {e}")
            continue

        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        if not m:
            continue

        try:
            data = json.loads(m.group(1))
            raw_jobs = data.get("props", {}).get("pageProps", {}).get("jobs", [])
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            _log(f"Hiredly JSON 解析失败: {e}")
            continue

        for raw in raw_jobs:
            if raw.get("expired"):
                continue
            title = raw.get("title", "")
            # Filter: only chef/kitchen/restaurant roles (not QA/Admin etc for non-ground page)
            is_ground = "food-beverage-on-ground" in url
            if not is_ground and not any(kw in title.lower() for kw in JOB_KEYWORDS):
                continue
            # For ground page, include all jobs (they're all F&B on-ground)
            company = raw.get("company", {}).get("name", "")
            salary_raw = raw.get("salary", "")
            salary = _parse_salary(f"RM {salary_raw}" if salary_raw and salary_raw != "Undisclosed" else None)
            location = raw.get("location", "Johor")
            date_iso = raw.get("activeAt", "")
            date = date_iso[:10] if date_iso else datetime.now(MYT).strftime("%Y-%m-%d")
            slug = raw.get("slug", "")
            job_url = f"https://my.hiredly.com/{slug}" if slug else url

            jobs.append({
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
                "salary": salary,
                "date": date,
                "url": job_url,
                "source": "Hiredly",
            })

    _log(f"Hiredly: {len(jobs)} 条")
    return jobs


# ── Maukerja (Playwright) ──────────────────────────────────────────────

def _browser_scrape(url: str, extract_js: str) -> list:
    """Generic helper: load page in Playwright, run JS extractor"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="ms-MY",
        )
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="load", timeout=15000)
            time.sleep(2)  # Let dynamic content settle
            result = page.evaluate(extract_js)
            return result or []
        except Exception as e:
            _log(f"Playwright 抓取失败 [{url}]: {e}")
            return []
        finally:
            browser.close()


def scrape_maukerja() -> list:
    """Scrape Maukerja.my via Playwright (Nuxt.js SSR -> DOM)"""
    extract_js = """
    () => {
      const items = [];
      document.querySelectorAll('a[href*="/job/"].is-hidden-mobile').forEach(a => {
        let card = a;
        for (let i = 0; i < 4; i++) if (card && card.parentElement) card = card.parentElement;
        if (!card) return;
        const text = card.textContent;
        const title = a.textContent.trim();
        // Company: text before first salary/date marker
        let company = '';
        const lines = text.split('\\n').filter(l => l.trim().length > 3
          && !l.includes('MYR') && !l.includes('Posted') && !l.includes('MOHON')
          && !l.includes('save') && !l.includes('Baking') && !l.includes('Pastry')
          && !l.includes('Cooking') && !l.includes(',') && !l.includes('•')
          && !l.includes(title) && !l.includes('jobs in'));
        if (lines.length > 0) company = lines[0].trim().substring(0, 60);
        const s = text.match(/MYR([\\d,]+)\\s*-\\s*MYR([\\d,]+)/);
        const salary = s ? 'RM ' + s[1] + ' - RM ' + s[2] : '';
        const loc = card.querySelector('a[href*="location"]');
        const location = loc ? loc.textContent.trim() : 'Johor Bahru';
        const d = text.match(/Posted\\s+([\\d\\s\\w]+ago)/i);
        const dateText = d ? d[1].trim() : '';
        items.push({title, company, salary, location, date: dateText, link: a.href});
      });
      return items;
    }
    """
    raw = _browser_scrape(
        "https://www.maukerja.my/jobsearch/chef-jobs-in-johor-bahru",
        extract_js,
    )

    jobs = []
    for r in raw:
        jobs.append({
            "title": r.get("title", "").strip(),
            "company": r.get("company", "").strip(),
            "location": r.get("location", "Johor Bahru").strip(),
            "salary": _parse_salary(r.get("salary")),
            "date": _normalise_date(r.get("date", "")),
            "url": r.get("link", ""),
            "source": "Maukerja",
        })

    _log(f"Maukerja: {len(jobs)} 条")
    return jobs


# ── MyFutureJobs (Playwright) ─────────────────────────────────────────

def scrape_myfuturejobs() -> list:
    """Scrape MyFutureJobs.gov.my via Playwright (Angular SPA)"""
    extract_js = """
    () => {
      const items = [];
      // Infinite scroll - scroll to bottom to load all
      let lastH = 0, same = 0;
      const scroll = setInterval(() => {
        window.scrollTo(0, document.body.scrollHeight);
        const h = document.body.scrollHeight;
        if (h === lastH) { same++; } else { same = 0; lastH = h; }
        if (same > 3) clearInterval(scroll);
      }, 500);
      // Wait for scroll completion (approximate)
      return new Promise(resolve => {
        setTimeout(() => {
          document.querySelectorAll('[data-test="swipe-vacancySummary-title"], .vacancy-summary-02__position-title').forEach(el => {
            const card = el.closest('a') || el.closest('[class*="list__item"]');
            if (!card) return;
            const title = el.textContent.trim();
            const company = (card.querySelector('[data-test="swipe-vacancySummary-company--name"]') || card.querySelector('.vacancy-summary-02__company-name'))?.textContent.trim() || '';
            const location = (card.querySelector('[data-test="swipe-vacancySummary-company--location"]') || card.querySelector('.vacancy-summary-02__company-location'))?.textContent.trim() || 'Johor Bahru';
            const footer = (card.querySelector('[data-test="swipe-vacancySummary-company--footer"]') || card.querySelector('.vacancy-summary-02__company-info-footer'))?.textContent.trim() || '';
            const href = card.getAttribute('href') || '';
            const link = href.startsWith('http') ? href : 'https://candidates.myfuturejobs.gov.my' + href;
            items.push({title, company, location, date: footer, link});
          });
          resolve(items);
        }, 5000);
      });
    }
    """
    raw = _browser_scrape(
        "https://candidates.myfuturejobs.gov.my/search-jobs?what=chef&where=Johor%20Bahru",
        extract_js,
    )

    jobs = []
    for r in raw:
        title = r.get("title", "")
        if not any(kw in title.lower() for kw in JOB_KEYWORDS):
            continue
        salary = r.get("salary")  # Salary is on detail page, not listing
        jobs.append({
            "title": title.strip(),
            "company": r.get("company", "").strip(),
            "location": r.get("location", "Johor Bahru").strip(),
            "salary": _parse_salary(salary),
            "date": _normalise_date(r.get("date", "")),
            "url": r.get("link", ""),
            "source": "MyFutureJobs",
        })

    _log(f"MyFutureJobs: {len(jobs)} 条")
    return jobs


# ── Aggregator ────────────────────────────────────────────────────────

def scrape_all():
    """Run all scrapers, combine, dedup, and write output"""
    all_jobs = []
    all_jobs.extend(scrape_jora(max_pages=4))
    all_jobs.extend(scrape_hiredly())
    all_jobs.extend(scrape_maukerja())
    try:
        mfj = scrape_myfuturejobs()
        all_jobs.extend(mfj)
    except Exception as e:
        _log(f"MyFutureJobs 错误: {e}")

    all_jobs = _dedup_jobs(all_jobs)

    _log(f"共 {len(all_jobs)} 条 (去重后)")

    # Enrich all jobs with AI-searchable fields
    for job in all_jobs:
        _enrich_job(job)

    all_jobs.sort(key=lambda x: x.get("date", ""), reverse=True)

    now = datetime.now(MYT)
    output = {
        "updated": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "count": len(all_jobs),
        "by_source": {},
        "items": all_jobs,
    }

    for j in all_jobs:
        src = j.get("source", "unknown")
        output["by_source"][src] = output["by_source"].get(src, 0) + 1

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)
    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "jobs.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    by_src = ", ".join(f"{k}={v}" for k, v in output["by_source"].items())
    print(f"✅ 招聘聚合完成: {len(all_jobs)} 条 ({by_src})")
    return f"{len(all_jobs)} 条 ({by_src})"


if __name__ == "__main__":
    scrape_all()
