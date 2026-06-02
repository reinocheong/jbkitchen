#!/usr/bin/env python3
"""
jbkitchen — 新闻聚合器
薄层封装：过滤 + 写 JSON
"""

import os, json
from datetime import datetime
from zoneinfo import ZoneInfo

from news_filter import build_news

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
SH_TZ = ZoneInfo("Asia/Shanghai")


def collect_news():
    news = build_news()
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    for d in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(d, "news.json"), "w", encoding="utf-8") as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
        with open(os.path.join(d, "news_meta.json"), "w", encoding="utf-8") as f:
            json.dump({
                "count": len(news),
                "updated": datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M"),
            }, f, ensure_ascii=False, indent=2)

    return f"{len(news)} 条新闻"


if __name__ == "__main__":
    result = collect_news()
    print(f"✅ {result}")
