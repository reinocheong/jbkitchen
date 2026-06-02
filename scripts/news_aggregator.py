#!/usr/bin/env python3
"""
jbkitchen — 行业新闻聚合器
每天自动抓马来西亚餐饮/F&B 相关新闻，存到 data/ 供 Hugo 读取
"""

import os, sys, json, hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

try:
    import feedparser
except ImportError:
    os.system("pip install feedparser -q")
    import feedparser

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
SH_TZ = ZoneInfo("Asia/Shanghai")

# 餐饮/F&B 专用 RSS 源 — 已验证的 Feed
RSS_SOURCES = [
    {"name": "The Star Business", "url": "https://www.thestar.com.my/rss/business", "lang": "en"},
    {"name": "Malay Mail", "url": "https://www.malaymail.com/feed/rss/business", "lang": "en"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "lang": "en"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "lang": "en"},
]

# Hacker News 用关键词过滤餐饮相关
HN_KEYWORDS = ["restaurant", "food", "delivery", "kitchen", "cooking", "recipe", "grocery", "meal"]

# 餐饮关键词过滤
FB_KEYWORDS = [
    "restaurant", "food", "F&B", "cafe", "catering", "kitchen",
    "halal", "food delivery", "frozen food",
    "menu", "chef", "cook", "dining",
    "supplier", "批发",
    "inflation", "price", "cost",
    "马来西亚", "餐饮", "食品",
]

NON_FB_KEYWORDS = [
    "crypto", "bitcoin", "nft", "defence", "military", "election",
    "movie", "film", "music", "sport", "football",
]


def is_relevant(title, summary, source_name):
    text = (title + " " + summary).lower()

    # Hacker News 特殊处理
    if "Hacker News" in source_name:
        return any(kw in text for kw in HN_KEYWORDS)

    for nk in NON_FB_KEYWORDS:
        if nk.lower() in text:
            return False
    for kw in FB_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def collect_news():
    all_news = []
    seen_urls = set()

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            if not feed.entries:
                # 尝试用 requests 直接抓
                continue

            for entry in feed.entries[:15]:
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                summary = (entry.get("summary") or entry.get("description") or "")[:300]

                if not title or not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                if not is_relevant(title, summary, source["name"]):
                    continue

                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=SH_TZ)

                uid = hashlib.md5(link.encode()).hexdigest()[:10]
                all_news.append({
                    "id": uid,
                    "title": title,
                    "summary": summary[:200],
                    "url": link,
                    "source": source["name"],
                    "lang": source["lang"],
                    "published": published.isoformat() if published else "",
                    "collected_at": datetime.now(SH_TZ).isoformat(),
                })
        except Exception as e:
            print(f"  ⚠️ {source['name']}: {e}")

    # 如果 RSS 没拿到，用 Hacker News API 补充
    if len(all_news) < 5:
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search?query=food+restaurant+delivery&tags=story&hitsPerPage=10",
                timeout=10,
            )
            if resp.status_code == 200:
                for hit in resp.json().get("hits", []):
                    title = hit.get("title", "")
                    link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)
                    all_news.append({
                        "id": hashlib.md5(link.encode()).hexdigest()[:10],
                        "title": title,
                        "summary": "",
                        "url": link,
                        "source": "Hacker News",
                        "lang": "en",
                        "published": datetime.fromtimestamp(hit.get("created_at_i", 0), tz=SH_TZ).isoformat(),
                        "collected_at": datetime.now(SH_TZ).isoformat(),
                    })
        except:
            pass

    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    all_news = all_news[:50]

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "news.json"), "w", encoding="utf-8") as f:
            json.dump(all_news, f, ensure_ascii=False, indent=2)
        with open(os.path.join(dir_path, "news_meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "count": len(all_news),
                "updated": datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M"),
            }, f, ensure_ascii=False, indent=2)

    return f"{len(all_news)} 条新闻"


if __name__ == "__main__":
    result = collect_news()
    print(f"✅ {result}")
