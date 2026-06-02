#!/usr/bin/env python3
import urllib.request, json

# Malaysia CPI from World Bank
url = 'https://api.worldbank.org/v2/country/MY/indicator/FP.CPI.TOTL.ZG?format=json&per_page=5'
req = urllib.request.Request(url)
data = json.loads(urllib.request.urlopen(req).read().decode())
if len(data) > 1:
    print("=== Malaysia CPI (inflation %) ===")
    for item in data[1][:5]:
        year = item.get('date','?')
        value = item.get('value','N/A')
        print(f"  {year}: {value}%")

# Try to get food commodity price from World Bank pink sheet
# World Bank uses different indicators
indicators = [
    ("Food price index", "FP.CPI.TOTL.FOOD.IX"),
    ("Food import", "TM.VAL.FOOD.ZS.UN"),
]

for name, code in indicators:
    url2 = f"https://api.worldbank.org/v2/country/MY/indicator/{code}?format=json&per_page=3"
    req2 = urllib.request.Request(url2)
    try:
        data2 = json.loads(urllib.request.urlopen(req2).read().decode())
        if len(data2) > 1 and data2[1]:
            print(f"\n=== {name} ===")
            for item in data2[1][:3]:
                yr = item.get('date','?')
                val = item.get('value','N/A')
                print(f"  {yr}: {val}")
        else:
            print(f"\n❌ {name}: no data")
    except Exception as e:
        print(f"\n❌ {name}: {e}")
