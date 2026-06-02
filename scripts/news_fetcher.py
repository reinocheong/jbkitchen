#!/usr/bin/env python3
"""
jbkitchen — Google News RSS 新闻抓取器
从 Google News RSS 采集马来西亚餐饮/食材新闻，按类别组织
"""
import os, json
from datetime import datetime
from zoneinfo import ZoneInfo

import feedparser

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", ".logs")
SH_TZ = ZoneInfo("Asia/Shanghai")

# 22 search terms across 4 categories
SEARCH_TERMS = {
    "食材价格": [
        "harga makanan Malaysia 2026",
        "harga ayam Malaysia",
        "harga beras Malaysia",
        "harga sayur Malaysia",
        "harga minyak masak Malaysia",
        "harga telur Malaysia",
    ],
    "政策法令": [
        "kerajaan subsidy makanan Malaysia",
        "sst perkhidmatan makanan Malaysia",
        "kementerian pertanian dasar makanan",
        "halal certification Malaysia 2026",
        "minimum wage Malaysia F&B",
        "harga siling ayam Malaysia",
    ],
    "行业趋势": [
        "industri makanan Malaysia trend",
        "digitalisasi restoran Malaysia",
        "food delivery Malaysia 2026",
        "perniagaan makanan Malaysia",
        "francais makanan Malaysia",
        "restoran baru Johor Bahru",
    ],
    "新山本地": [
        "Johor Bahru food news",
        "JB restoran baru",
        "Johor pelancongan makanan",
        "ekonomi Johor Bahru 2026",
    ],
}


def _log_error(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "error.log"), "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [news_fetcher] {msg}\n")


def _fetch_rss(search_term):
    """Fetch RSS entries for a single search term from Google News"""
    import urllib.parse

    encoded = urllib.parse.quote(search_term)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-MY&gl=MY&ceid=MY:en"

    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:3]:
            entries.append({
                "title": (entry.get("title") or "").strip(),
                "url": (entry.get("link") or "").strip(),
                "source": _extract_source(entry),
                "published": _parse_date(entry),
                "summary": _extract_summary(entry),
            })
        return entries
    except Exception as e:
        _log_error(f"RSS 抓取失败 [{search_term}]: {e}")
        return []


def _extract_source(entry):
    """Extract source name from RSS entry"""
    source = entry.get("source", {})
    if isinstance(source, dict):
        return source.get("title", "") or source.get("href", "") or ""
    return ""


def _extract_summary(entry):
    """Extract and clean summary text"""
    raw = entry.get("summary") or entry.get("description") or ""
    # Strip HTML tags
    import re
    clean = re.sub(r"<[^>]+>", "", raw)
    # Truncate
    if len(clean) > 200:
        clean = clean[:197] + "..."
    return clean.strip()


def _parse_date(entry):
    """Parse published date, return YYYY-MM-DD string"""
    from email.utils import parsedate_to_datetime

    published = entry.get("published", "")
    if published:
        try:
            dt = parsedate_to_datetime(published)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    return datetime.now(SH_TZ).strftime("%Y-%m-%d")


def _deduplicate(items):
    """Remove duplicates by URL, then by title similarity"""
    seen_urls = set()
    seen_titles = set()
    result = []
    for item in items:
        url = item.get("url", "")
        title = item.get("title", "").lower().strip()
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        result.append(item)
    return result


def fetch_news(max_items=30):
    """Main entry: fetch all news, deduplicate, output JSON"""
    all_items = []

    for category, terms in SEARCH_TERMS.items():
        for term in terms:
            entries = _fetch_rss(term)
            for entry in entries:
                entry["category"] = category
            all_items.extend(entries)

    # Deduplicate
    all_items = _deduplicate(all_items)

    # Sort by published date descending
    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)

    # Limit
    all_items = all_items[:max_items]

    output = {
        "updated": datetime.now(SH_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
        "items": all_items,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "news.json"), "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    return f"{len(all_items)} 条新闻"


if __name__ == "__main__":
    result = fetch_news()
    print(f"✅ {result}")
