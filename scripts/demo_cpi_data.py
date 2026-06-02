#!/usr/bin/env python3
import csv, urllib.request, io

# Download CPI 5-digit data
url = 'https://storage.dosm.gov.my/cpi/cpi_5d.csv'
req = urllib.request.Request(url)
data = urllib.request.urlopen(req, timeout=30).read().decode()

# Download MCOICOP lookup
url2 = 'https://storage.dosm.gov.my/dictionaries/mcoicop.csv'
req2 = urllib.request.Request(url2)
lookup_data = urllib.request.urlopen(req2, timeout=30).read().decode()

# Build lookup dict
lookup = {}
for row in csv.DictReader(io.StringIO(lookup_data)):
    if row['subclass'] and row['subclass'].strip():
        lookup[row['subclass'].strip()] = row['desc_en'].strip()

# Food codes we track
food_codes = {
    '00111': '外出用餐指数',
    '01111': '米/谷物',
    '01122': '肉类(鸡猪牛)',
    '01131': '鱼类',
    '01141': '蛋奶类',
    '01151': '食用油',
    '01171': '蔬菜',
    '01181': '糖',
}

# Get data
reader = csv.DictReader(io.StringIO(data))
prices = {}
prev = {}
for row in reader:
    sc = row['subclass']
    if sc in food_codes and row['date'].endswith('-04-01'):
        if row['date'] == '2026-04-01':
            prices[sc] = float(row['index'])
        elif row['date'] == '2025-04-01':
            prev[sc] = float(row['index'])

print('=== 马来西亚官方物价指数（政府统计局 DOSM）===')
print('来源: 消费者价格指数(CPI) 5位码数据')
print('基年: 2010=100 | 数据: 2026年4月\n')

print('食材分类             指数   年变化')
print('-' * 45)
for code, name in food_codes.items():
    if code in prices:
        c = prices[code]
        p = prev.get(code, c)
        chg = ((c - p) / p) * 100
        arrow = chr(9650) if chg > 0 else chr(9660)
        print(f'{name:<16} {c:>8.1f}  {arrow} {abs(chg):.1f}%')

print('\n注: 年变化 = 2026年4月 vs 2025年4月 同比')
print('数据来源: Department of Statistics Malaysia (DOSM)')
