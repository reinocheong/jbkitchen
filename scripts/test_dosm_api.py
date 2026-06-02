# ⛔ DEPRECATED - 探索/测试脚本，aggregate.py 未引用此文件，请勿使用
1|#!/usr/bin/env python3
2|import urllib.request, json, sys
3|
4|datasets = ["cpi_3d", "cpi_4d", "cpi_5d", "cpi_headline", "cpi_state", "cpi_core"]
5|
6|for d in datasets:
7|    url = f"https://api.data.gov.my/opendosm?id={d}&limit=5"
8|    try:
9|        req = urllib.request.Request(url)
10|        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
11|        if isinstance(data, list):
12|            print(f"=== {d} === ({len(data)} items)")
13|            for item in data[:3]:
14|                print(f"  {json.dumps(item)[:150]}")
15|        else:
16|            print(f"=== {d} === {str(data)[:150]}")
17|    except Exception as e:
18|        print(f"=== {d} === Error: {e}")
19|    print()
20|