#!/usr/bin/env python3
"""
jbkitchen — 汇率+食材价格追踪
免费 API 获取 MYR 汇率和商品价格
"""

import os, json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "data")
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", ".logs")
SH_TZ = ZoneInfo("Asia/Shanghai")


def _log_error(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "error.log"), "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [price_tracker] {msg}\n")


def track_prices():
    prices = {
        "updated": datetime.now(SH_TZ).strftime("%Y-%m-%d %H:%M"),
        "fx": {},
        "commodities": {},
    }

    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/MYR", timeout=10)
        if resp.status_code == 200:
            rates = resp.json().get("rates", {})
            prices["fx"] = {
                "MYR_USD": round(1 / rates.get("USD", 1), 4),
                "MYR_CNY": round(1 / rates.get("CNY", 1), 4),
                "MYR_SGD": round(1 / rates.get("SGD", 1), 4),
                "USD_MYR": round(rates.get("USD", 0), 4),
            }
    except Exception as e:
        _log_error(f"汇率获取失败: {e}")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "prices.json"), "w", encoding="utf-8") as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)

    return f"USD/MYR={prices['fx'].get('USD_MYR', '?')}"


if __name__ == "__main__":
    r = track_prices()
    print(f"✅ {r}")
