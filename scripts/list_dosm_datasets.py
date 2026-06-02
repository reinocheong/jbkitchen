# ⛔ DEPRECATED - 探索/测试脚本，aggregate.py 未引用此文件，请勿使用
1|#!/usr/bin/env python3
2|import subprocess, json, sys
3|
4|# Fetch all datasets from DOSM catalogue
5|result = subprocess.run(
6|    ['curl', '-sL', '--max-time', '15', 'https://api.data.gov.my/catalogue?id=opendosm&limit=200'],
7|    capture_output=True, timeout=20
8|)
9|
10|try:
11|    data = json.loads(result.stdout)
12|    if isinstance(data, list):
13|        for item in data:
14|            name = item.get('name', '?')
15|            desc = item.get('description', '')[:100]
16|            data_id = item.get('id', '?')
17|            agency = item.get('agency', '')
18|            print(f'{data_id}: {agency} - {desc}')
19|    else:
20|        print(data)
21|except Exception as e:
22|    print(f'Error: {e}')
23|    print(result.stdout[:1000])
24|