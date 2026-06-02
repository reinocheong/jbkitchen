#!/usr/bin/env python3
import subprocess, json, sys

# Fetch all datasets from DOSM catalogue
result = subprocess.run(
    ['curl', '-sL', '--max-time', '15', 'https://api.data.gov.my/catalogue?id=opendosm&limit=200'],
    capture_output=True, timeout=20
)

try:
    data = json.loads(result.stdout)
    if isinstance(data, list):
        for item in data:
            name = item.get('name', '?')
            desc = item.get('description', '')[:100]
            data_id = item.get('id', '?')
            agency = item.get('agency', '')
            print(f'{data_id}: {agency} - {desc}')
    else:
        print(data)
except Exception as e:
    print(f'Error: {e}')
    print(result.stdout[:1000])
