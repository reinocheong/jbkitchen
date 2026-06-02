# ⛔ DEPRECATED - 探索/测试脚本，aggregate.py 未引用此文件，请勿使用
1|#!/usr/bin/env python3
2|import urllib.request, json
3|
4|# Malaysia CPI from World Bank
5|url = 'https://api.worldbank.org/v2/country/MY/indicator/FP.CPI.TOTL.ZG?format=json&per_page=5'
6|req = urllib.request.Request(url)
7|data = json.loads(urllib.request.urlopen(req).read().decode())
8|if len(data) > 1:
9|    print("=== Malaysia CPI (inflation %) ===")
10|    for item in data[1][:5]:
11|        year = item.get('date','?')
12|        value = item.get('value','N/A')
13|        print(f"  {year}: {value}%")
14|
15|# Try to get food commodity price from World Bank pink sheet
16|# World Bank uses different indicators
17|indicators = [
18|    ("Food price index", "FP.CPI.TOTL.FOOD.IX"),
19|    ("Food import", "TM.VAL.FOOD.ZS.UN"),
20|]
21|
22|for name, code in indicators:
23|    url2 = f"https://api.worldbank.org/v2/country/MY/indicator/{code}?format=json&per_page=3"
24|    req2 = urllib.request.Request(url2)
25|    try:
26|        data2 = json.loads(urllib.request.urlopen(req2).read().decode())
27|        if len(data2) > 1 and data2[1]:
28|            print(f"\n=== {name} ===")
29|            for item in data2[1][:3]:
30|                yr = item.get('date','?')
31|                val = item.get('value','N/A')
32|                print(f"  {yr}: {val}")
33|        else:
34|            print(f"\n❌ {name}: no data")
35|    except Exception as e:
36|        print(f"\n❌ {name}: {e}")
37|