#!/usr/bin/env python3
import urllib.request, re

commodities = ['chicken', 'rice', 'palm-oil', 'sugar', 'soybean-oil', 'wheat']
for c in commodities:
    url = f'https://www.indexmundi.com/commodities/?commodity={c}&months=1'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read().decode()
        # Find current price (often in a chart or summary)
        prices = re.findall(r'\$[0-9.,]+', html)
        names = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        name = names[0].strip() if names else c
        if prices:
            print(f'✅ {name}: {prices[0]}')
        else:
            print(f'❌ {c}: no price')
    except Exception as e:
        print(f'❌ {c}: {e}')
