#!/usr/bin/env python3
"""
jbkitchen — 主聚合器
每日运行，采集新闻 + 价格数据 + 生成 JSON
"""

import os, sys, json, shutil
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
from news_aggregator import collect_news
from price_tracker import track_prices

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", ".logs")
SH_TZ = ZoneInfo("Asia/Shanghai")


def _log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "error.log"), "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def sync_to_site():
    os.makedirs(SITE_DATA_DIR, exist_ok=True)
    count = 0
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            shutil.copy2(os.path.join(DATA_DIR, fname), os.path.join(SITE_DATA_DIR, fname))
            count += 1
    return f"同步 {count} 个文件"


def main():
    now = datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 jbkitchen 数据聚合 - {now}")
    print("=" * 40)

    results = {}

    print("\n📰 采集新闻...")
    try:
        r = collect_news()
        results["news"] = f"✅ {r}"
        print(f"  → {r}")
    except Exception as e:
        _log(f"collect_news 失败: {e}")
        results["news"] = f"❌ {e}"

    print("\n💱 获取价格...")
    try:
        r = track_prices()
        results["prices"] = f"✅ {r}"
        print(f"  → {r}")
    except Exception as e:
        _log(f"track_prices 失败: {e}")
        results["prices"] = f"❌ {e}"

    print("\n📦 同步数据...")
    r = sync_to_site()
    results["sync"] = f"✅ {r}"

    meta = {"last_update": datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S"), "results": results}
    for d in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(d, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    ok = sum(1 for v in results.values() if v.startswith("✅"))
    fail = sum(1 for v in results.values() if v.startswith("❌"))
    print(f"\n📊 {ok} 成功 / {fail} 失败")


if __name__ == "__main__":
    main()
