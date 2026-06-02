#!/usr/bin/env python3
"""
jbkitchen — 汇率+CPI 价格追踪
免费 API 获取 MYR 汇率和 DOSM 官方 CPI 数据
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


# COICOP division mapping (only divisions verified in API)
DIVISION_MAP = {
    "overall": ("overall", "整体通胀"),
    "01": ("food_beverages", "食品与饮料"),
    "04": ("housing", "住房水电"),
    "07": ("transport", "交通"),
    "08": ("communication", "通讯"),
}


def _fetch_cpi():
    """Fetch latest CPI index and inflation data from DOSM"""
    cpi = {}

    try:
        # CPI headline index
        resp = requests.get(
            "https://api.data.gov.my/opendosm?id=cpi_headline&limit=5000",
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                # Find latest date
                latest_date = max(item.get("date", "") for item in data if item.get("date"))
                # Build index map for latest date
                for item in data:
                    if item.get("date") == latest_date:
                        div = item.get("division", "")
                        idx = item.get("index")
                        if div in DIVISION_MAP and idx is not None:
                            key, label = DIVISION_MAP[div]
                            cpi[key] = {"index": idx, "label": label}
                cpi["_date"] = latest_date
    except Exception as e:
        _log_error(f"CPI index 获取失败: {e}")

    try:
        # CPI inflation (YoY)
        resp = requests.get(
            "https://api.data.gov.my/opendosm?id=cpi_headline_inflation&limit=5000",
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                latest_date = max(item.get("date", "") for item in data if item.get("date"))
                for item in data:
                    if item.get("date") == latest_date:
                        div = item.get("division", "")
                        inf = item.get("inflation_yoy")
                        if div in DIVISION_MAP and inf is not None:
                            key, _ = DIVISION_MAP[div]
                            if key in cpi:
                                cpi[key]["inflation_yoy"] = inf
    except Exception as e:
        _log_error(f"CPI inflation 获取失败: {e}")

    return cpi


def _fetch_fx():
    """Fetch MYR exchange rates from exchangerate-api.com"""
    fx = {}
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/MYR", timeout=10)
        if resp.status_code == 200:
            rates = resp.json().get("rates", {})
            usd = rates.get("USD", 0)
            cny = rates.get("CNY", 0)
            sgd = rates.get("SGD", 0)
            fx = {
                "USD_MYR": round(1 / usd, 4) if usd else 0,
                "MYR_USD": round(usd, 4),
                "CNY_MYR": round(1 / cny, 4) if cny else 0,
                "SGD_MYR": round(1 / sgd, 4) if sgd else 0,
            }
    except Exception as e:
        _log_error(f"汇率获取失败: {e}")
    return fx


def track_prices():
    prices = {
        "updated": datetime.now(SH_TZ).strftime("%Y-%m-%d"),
        "fx": _fetch_fx(),
        "cpi": {},
    }

    cpi_data = _fetch_cpi()
    cpi_date = cpi_data.pop("_date", datetime.now(SH_TZ).strftime("%Y-%m-%d"))

    # Build ordered CPI output
    cpi_order = ["overall", "food_beverages", "housing", "transport", "communication"]
    for key in cpi_order:
        if key in cpi_data:
            prices["cpi"][key] = cpi_data[key]

    if cpi_data:
        prices["updated"] = cpi_date

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    for dir_path in [DATA_DIR, SITE_DATA_DIR]:
        with open(os.path.join(dir_path, "prices.json"), "w", encoding="utf-8") as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)

    fx_str = f"USD/MYR={prices['fx'].get('USD_MYR', '?')}"
    cpi_str = f"CPI overall={prices['cpi'].get('overall', {}).get('inflation_yoy', '?')}%"
    return f"{fx_str} | {cpi_str}"


if __name__ == "__main__":
    r = track_prices()
    print(f"✅ {r}")
