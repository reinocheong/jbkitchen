#!/usr/bin/env python3
import urllib.request, json, sys

datasets = ["cpi_3d", "cpi_4d", "cpi_5d", "cpi_headline", "cpi_state", "cpi_core"]

for d in datasets:
    url = f"https://api.data.gov.my/opendosm?id={d}&limit=5"
    try:
        req = urllib.request.Request(url)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if isinstance(data, list):
            print(f"=== {d} === ({len(data)} items)")
            for item in data[:3]:
                print(f"  {json.dumps(item)[:150]}")
        else:
            print(f"=== {d} === {str(data)[:150]}")
    except Exception as e:
        print(f"=== {d} === Error: {e}")
    print()
