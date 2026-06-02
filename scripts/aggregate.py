#!/usr/bin/env python3
"""jbkitchen — 数据聚合调度"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from news_fetcher import fetch_news
from price_tracker import track_prices


def aggregate():
    r1 = fetch_news()
    r2 = track_prices()
    print(f"✅ 聚合完成: {r1} | {r2}")


if __name__ == "__main__":
    aggregate()
