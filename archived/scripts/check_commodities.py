# ⛔ DEPRECATED - 探索/测试脚本，aggregate.py 未引用此文件，请勿使用
1|#!/usr/bin/env python3
2|import urllib.request, re
3|
4|commodities = ['chicken', 'rice', 'palm-oil', 'sugar', 'soybean-oil', 'wheat']
5|for c in commodities:
6|    url = f'https://www.indexmundi.com/commodities/?commodity={c}&months=1'
7|    try:
8|        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
9|        html = urllib.request.urlopen(req, timeout=10).read().decode()
10|        # Find current price (often in a chart or summary)
11|        prices = re.findall(r'\$[0-9.,]+', html)
12|        names = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
13|        name = names[0].strip() if names else c
14|        if prices:
15|            print(f'✅ {name}: {prices[0]}')
16|        else:
17|            print(f'❌ {c}: no price')
18|    except Exception as e:
19|        print(f'❌ {c}: {e}')
20|