#!/usr/bin/env python3
"""
jbkitchen — RSS 新闻抓取器
负责：从各 RSS 源抓取原始新闻条目
"""

import os
import feedparser

RSS_SOURCES = [
    {"name": "The Star Business", "url": "https://www.thestar.com.my/rss/business", "lang": "en"},
    {"name": "Malay Mail", "url": "https://www.malaymail.com/feed/rss/business", "lang": "en"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "lang": "en"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "lang": "en"},
]


def fetch_all():
    """从所有 RSS 源抓取原始条目，返回 list of dict"""
    entries = []
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:15]:
                entries.append({
                    "title": (entry.get("title") or "").strip(),
                    "link": (entry.get("link") or "").strip(),
                    "summary": (entry.get("summary") or entry.get("description") or "")[:300],
                    "source": source["name"],
                    "lang": source["lang"],
                })
        except Exception as e:
            err_msg = f"[RSS]{source['name']} fetch failed: {e}"
            print(f"  ⚠️ {err_msg}")
            _log_error(err_msg)
    return entries


def _log_error(msg):
    """写错误日志"""
    from datetime import datetime
    log_dir = os.path.join(os.path.dirname(__file__), "..", ".logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "error.log"), "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
