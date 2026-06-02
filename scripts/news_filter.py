# ⛔ DEPRECATED — 关联 news_aggregator.py，均被 news_fetcher.py 替代
#!/usr/bin/env python3
"""
jbkitchen — (DEPRECATED) 新闻过滤器
负责：餐饮关键词过滤、API 补充、去重
"""

import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from news_fetcher import fetch_all, _log_error

SH_TZ = ZoneInfo("Asia/Shanghai")

HN_KEYWORDS = ["restaurant", "food", "delivery", "kitchen", "cooking", "grocery", "meal"]
FB_KEYWORDS = [
    "restaurant", "food", "F&B", "cafe", "catering", "kitchen",
    "halal", "food delivery", "frozen food",
    "menu", "chef", "cook", "dining", "supplier",
    "inflation", "price", "cost", "批发",
    "马来西亚", "餐饮", "食品",
]
NON_FB_KEYWORDS = [
    "crypto", "bitcoin", "nft", "defence", "military", "election",
    "movie", "film", "music", "sport", "football",
]


def is_relevant(title, summary, source_name):
    text = (title + " " + summary).lower()
    if "Hacker News" in source_name:
        return any(kw in text for kw in HN_KEYWORDS)
    for nk in NON_FB_KEYWORDS:
        if nk.lower() in text:
            return False
    return any(kw.lower() in text for kw in FB_KEYWORDS)


def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        result.append(item)
    return result


def _hn_api_fallback(seen_urls):
    """Hacker News Algolia API 补充"""
    items = []
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search?query=food+restaurant+delivery&tags=story&hitsPerPage=10",
            timeout=10,
        )
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                if url in seen_urls:
                    continue
                items.append({
                    "title": hit.get("title", ""),
                    "url": url,
                    "summary": "",
                    "source": "Hacker News",
                    "lang": "en",
                    "published": datetime.fromtimestamp(hit.get("created_at_i", 0), tz=SH_TZ).isoformat(),
                })
    except Exception as e:
        _log_error(f"HN API fallback failed: {e}")
    return items


def build_news() -> list:
    """完整流程：抓 → 过滤 → 去重 → 补充 → 排序"""
    raw = fetch_all()
    print(f"  [filter] 抓到 {len(raw)} 条原始数据")

    filtered = []
    seen_urls = set()
    for entry in raw:
        if not entry["title"] or not entry["link"]:
            continue
        if entry["link"] in seen_urls:
            continue
        if not is_relevant(entry["title"], entry["summary"], entry["source"]):
            continue
        seen_urls.add(entry["link"])
        uid = hashlib.md5(entry["link"].encode()).hexdigest()[:10]
        filtered.append({
            "id": uid,
            "title": entry["title"],
            "summary": entry["summary"][:200],
            "url": entry["link"],
            "source": entry["source"],
            "lang": entry["lang"],
            "published": "",
            "collected_at": datetime.now(SH_TZ).isoformat(),
        })

    print(f"  [filter] 过滤后 {len(filtered)} 条")

    if len(filtered) < 5:
        hn_items = _hn_api_fallback(seen_urls)
        for item in hn_items:
            uid = hashlib.md5(item["url"].encode()).hexdigest()[:10]
            item["id"] = uid
            item["collected_at"] = datetime.now(SH_TZ).isoformat()
        filtered.extend(hn_items)
        print(f"  [filter] HN API 补充 {len(hn_items)} 条")

    filtered.sort(key=lambda x: x.get("published", ""), reverse=True)
    return filtered[:50]
