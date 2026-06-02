# ⛔ DEPRECATED - 探索/测试脚本，aggregate.py 未引用此文件，请勿使用
1|#!/usr/bin/env python3
2|import csv, urllib.request, io
3|
4|# Download CPI 5-digit data
5|url = 'https://storage.dosm.gov.my/cpi/cpi_5d.csv'
6|req = urllib.request.Request(url)
7|data = urllib.request.urlopen(req, timeout=30).read().decode()
8|
9|# Download MCOICOP lookup
10|url2 = 'https://storage.dosm.gov.my/dictionaries/mcoicop.csv'
11|req2 = urllib.request.Request(url2)
12|lookup_data = urllib.request.urlopen(req2, timeout=30).read().decode()
13|
14|# Build lookup dict
15|lookup = {}
16|for row in csv.DictReader(io.StringIO(lookup_data)):
17|    if row['subclass'] and row['subclass'].strip():
18|        lookup[row['subclass'].strip()] = row['desc_en'].strip()
19|
20|# Food codes we track
21|food_codes = {
22|    '00111': '外出用餐指数',
23|    '01111': '米/谷物',
24|    '01122': '肉类(鸡猪牛)',
25|    '01131': '鱼类',
26|    '01141': '蛋奶类',
27|    '01151': '食用油',
28|    '01171': '蔬菜',
29|    '01181': '糖',
30|}
31|
32|# Get data
33|reader = csv.DictReader(io.StringIO(data))
34|prices = {}
35|prev = {}
36|for row in reader:
37|    sc = row['subclass']
38|    if sc in food_codes and row['date'].endswith('-04-01'):
39|        if row['date'] == '2026-04-01':
40|            prices[sc] = float(row['index'])
41|        elif row['date'] == '2025-04-01':
42|            prev[sc] = float(row['index'])
43|
44|print('=== 马来西亚官方物价指数（政府统计局 DOSM）===')
45|print('来源: 消费者价格指数(CPI) 5位码数据')
46|print('基年: 2010=100 | 数据: 2026年4月\n')
47|
48|print('食材分类             指数   年变化')
49|print('-' * 45)
50|for code, name in food_codes.items():
51|    if code in prices:
52|        c = prices[code]
53|        p = prev.get(code, c)
54|        chg = ((c - p) / p) * 100
55|        arrow = chr(9650) if chg > 0 else chr(9660)
56|        print(f'{name:<16} {c:>8.1f}  {arrow} {abs(chg):.1f}%')
57|
58|print('\n注: 年变化 = 2026年4月 vs 2025年4月 同比')
59|print('数据来源: Department of Statistics Malaysia (DOSM)')
60|