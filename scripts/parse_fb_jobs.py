#!/usr/bin/env python3
"""Parse FB job group raw posts into structured job listings"""
import os, re, json, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import enrichment from scrape_jobs
sys.path.insert(0, os.path.dirname(__file__))
from scrape_jobs import _enrich_job

RAW_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "fb_jobs_raw.json")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MYT = ZoneInfo("Asia/Kuala_Lumpur")

JOB_KEYWORDS = [
    'chef', 'cook', 'kitchen', 'tukang masak', 'pembantu dapur',
    'commis', 'demi chef', 'sous chef', 'pastry', 'baker',
    'food', 'restoran', 'restaurant', 'cafe', 'f&b', 'fb',
    'masak', 'dapur', 'kitchen crew', 'barista', 'pelayan',
    'waiter', 'waitress', 'captain', 'hotel',
]


def clean_fb_text(text):
    """Strip Facebook UI noise from post text"""
    if not text:
        return ""

    # Remove "X月X日HH:MM · 分享对象" patterns
    text = re.sub(r'\d{1,2}月\d{1,2}日\d{1,2}:\d{2}\s*[·\-]\s*分享对象[：:][^。\n]*', '', text)

    # Remove "所有心情：N" and everything after
    text = re.split(r'所有心情[：:]\s*\d+', text)[0]

    # Remove "N条评论" and everything after
    text = re.split(r'\d+\s*条评论', text)[0]

    # Remove reaction/comment fragments
    for frag in ['赞评论分享', '赞回复分享', '查看更多回答', '查看更多评论',
                 '以 Reino Cheong 的身份回答', '以 Reino Cheong 的身份评论',
                 '查看翻译', '原声', '展开']:
        text = text.replace(frag, ' ')

    # Remove timestamps like "5月19日13:11"
    text = re.sub(r'\d{1,2}月\d{1,2}日\d{1,2}:\d{2}', '', text)

    # Remove "N周赞回复分享" patterns
    text = re.sub(r'\d+\s*(周|天|小时|分钟)\s*(前|ago).*$', '', text)

    # Remove user mentions at end
    text = re.sub(r'\S+\s+回复了\s*[·]\s*\d+条回复', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def extract_job_info(text):
    """Extract job title, company, salary, location from post text"""
    text_lower = text.lower()
    cleaned = clean_fb_text(text)

    if not cleaned or len(cleaned) < 20:
        return None

    # Skip if not relevant
    if not any(kw in text_lower for kw in JOB_KEYWORDS):
        return None

    result = {
        "title": cleaned[:80],  # Use whole text as title initially
        "company": "",
        "location": "Johor Bahru",
        "salary": None,
        "date": datetime.now(MYT).strftime("%Y-%m-%d"),
    }

    # Try to extract specific job title
    job_patterns = [
        r'(?:jawatan\s+)?(?:kosong\s+)?(?:pekerja\s+)?(?:utk\s+)?(?:seperti\s*)?\d?\)?\s*(TUKANG MASAK|CHEF|COOK|PASTRY|BAKER|DEMI CHEF|SOUS CHEF|KITCHEN CREW|BARISTA|PELAYAN|WAITER|WAITRESS|PEMBANTU DAPUR|KITCHEN|COMMIS)',
        r'(?:Looking for|Hiring|Required|Urgent| diperlukan|vacancy)\s*(?:a\s+)?(.{5,40}?)(?:\s+in\s+|\s+for\s+|\.|$)',
    ]
    for pat in job_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result["title"] = m.group(1).strip().title()
            break

    # Extract phone number (Malaysia)
    phone = ""
    phone_pat = r'(?:0\d[-\s]?\d{7,8}|\+60[-\s]?\d{1,2}[-\s]?\d{7,8}|01\d[-\s]?\d{3,4}[-\s]?\d{4})'
    m = re.search(phone_pat, text)
    if m:
        phone = m.group(0).strip()

    # Extract salary
    salary_pat = r'(?:RM|MYR)\s*(\d[\d,]*)\s*(?:-\s*(?:RM|MYR)?\s*(\d[\d,]*))?'
    m = re.search(salary_pat, text, re.IGNORECASE)
    if m:
        s_min = m.group(1).replace(',', '')
        s_max = m.group(2).replace(',', '') if m.group(2) else None
        result["salary"] = {
            "min": int(s_min) if s_min else None,
            "max": int(s_max) if s_max else None,
            "period": "monthly",
            "text": m.group(0).strip(),
        }

    return {
        "title": result["title"][:100],
        "company": result["company"],
        "location": result["location"],
        "salary": result["salary"],
        "date": result["date"],
        "url": "",  # FB post link will be added below
        "source": "Facebook",
    }


def parse_fb_jobs():
    """Read raw FB posts, extract jobs, write to data dir"""
    if not os.path.exists(RAW_FILE):
        print("⚠️  fb_jobs_raw.json not found")
        return 0

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    if not raw_data:
        return 0

    jobs = []
    for post in raw_data:
        info = extract_job_info(post.get('text', ''))
        if info:
            info['url'] = post.get('link', '')
            info['fb_group'] = post.get('group_name', '')
            info = _enrich_job(info)
            jobs.append(info)

    output = {
        "updated": datetime.now(MYT).strftime("%Y-%m-%dT%H:%M:%S"),
        "count": len(jobs),
        "items": jobs,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    # Write to data dir for reference, but will be merged into main pipeline
    with open(os.path.join(DATA_DIR, "fb_jobs_parsed.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ FB 职位解析: {len(jobs)} 条")
    return jobs


if __name__ == "__main__":
    j = parse_fb_jobs()
    if j:
        for item in j:
            print(f"  - {item['title'][:60]} | {item['salary']['text'] if item['salary'] else '?'} | {item['source']}")
    else:
        print("没有找到职位")
