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
SH_TZ = ZoneInfo("Asia/Shanghai")


def sync_to_site():
    os.makedirs(SITE_DATA_DIR, exist_ok=True)
    count = 0
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            src = os.path.join(DATA_DIR, filename)
            dst = os.path.join(SITE_DATA_DIR, filename)
            shutil.copy2(src, dst)
            count += 1
    return f"同步 {count} 个文件"


def main():
    now = datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 jbkitchen 数据聚合 - {now}")
    print("=" * 40)

    results = {}

    # Phase 1: 新闻采集
    print("\n📰 采集新闻...")
    try:
        r = collect_news()
        results["news"] = f"✅ {r}"
        print(f"  → {r}")
    except Exception as e:
        results["news"] = f"❌ {e}"
        print(f"  → ❌ {e}")

    # Phase 2: 价格数据
    print("\n💱 获取价格...")
    try:
        r = track_prices()
        results["prices"] = f"✅ {r}"
        print(f"  → {r}")
    except Exception as e:
        results["prices"] = f"❌ {e}"
        print(f"  → ❌ {e}")

    # Phase 3: 同步到站点
    print("\n📦 同步数据...")
    r = sync_to_site()
    results["sync"] = f"✅ {r}"
    print(f"  → {r}")

    # 写入元数据
    meta = {
        "last_update": datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
    }
    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    success = sum(1 for v in results.values() if v.startswith("✅"))
    fail = sum(1 for v in results.values() if v.startswith("❌"))
    print(f"\n📊 {success} 成功 / {fail} 失败")


if __name__ == "__main__":
    main()
