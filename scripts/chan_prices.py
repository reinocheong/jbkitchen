#!/usr/bin/env python3
"""
jbkitchen — WhatsApp Channel 鸡价格解析
读取 chan_raw.json → 解析价格 → /0.9 → 进位 → 输出 chan_prices.json
"""
import os, re, json, math
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'site', 'data')
RAW_FILE = os.path.join(DATA_DIR, 'chan_raw.json')
OUT_FILE = os.path.join(DATA_DIR, 'chan_prices.json')

# Product name clarification mapping
PRODUCT_NAMES = {
    'bb': '去骨鸡胸肉',
    'boneless breast': '去骨鸡胸肉',
    'sbb': '去皮去骨鸡胸肉',
    'skinless boneless breast': '去皮去骨鸡胸肉',
    'bl': '去骨鸡腿肉',
    'boneless leg': '去骨鸡腿肉',
    'sbl': '去皮去骨鸡腿肉',
    'skinless boneless leg': '去皮去骨鸡腿肉',
    'wl': '全鸡腿',
    'whole leg': '全鸡腿',
    'whole chicken': '全鸡',
    'drumstick': '鸡腿 (Drumstick)',
    'mid joint wing': '鸡中翅',
    'wing': '鸡翅',
    'thigh': '鸡大腿肉',
    'fillet': '鸡柳肉',
    'chop': '鸡块 Chop',
    'spring': '童子鸡 (Spring)',
    'rib': '鸡肋骨',
    'buntut': '鸡屁股',
    'neck': '鸡颈',
    'pedal': '鸡脚',
    'kaki': '鸡脚',
    'rangka': '鸡骨架 (Carcass)',
    'carcass': '鸡骨架 (Carcass)',
    'chicken cube': '鸡肉丁',
    'oyster meat': '蚝肉鸡腿 (Oyster)',
    'keel': '鸡胸柳 (Keel)',
    'drummet': '小鸡腿 (Drummet)',
    'body skin': '鸡皮',
    'neck skin': '鸡颈皮',
    'cube': '鸡肉丁',
}

def round_to_10sen(val):
    """Round to nearest 0.10 (10 sen). 0.05 → up"""
    return math.floor(val * 10 + 0.5) / 10

def parse_price_line(line):
    """Parse a single line from the price list."""
    line = line.strip()
    if not line:
        return None
    
    # Skip non-item lines (discount info, address, etc.)
    skip_keywords = [
        'delivery', 'self-collect', 'operation hours', 'special discount',
        'puchong food', 'sila hubungi', 'sila hantar', 'for cash term',
        'kindly submit', 'terima kasih', 'thank you', 'half/full',
        'cash term', 'transport discount', 'container', 'please call',
        'no 4,', 'taman perindustrian', 'mon–fri', 'sat :'
    ]
    if any(kw in line.lower() for kw in skip_keywords):
        return None
    
    # Remove size ranges in parentheses that look like (0.8-0.9) or (0.65-0.85)
    # These are not prices, they're weight ranges
    line_clean = re.sub(r'\([\d.]+-[\d.]+\s*(?:kg)?\)', '', line, flags=re.IGNORECASE)
    
    # Also remove things like (11.12.13) - those are item size codes
    line_clean = re.sub(r'\([\d.]+\.[\d.]+\)', '', line_clean)
    
    # Check if line has a price
    # Price can be: 9.60, rm9.60, 9.00per nos, rm1.30
    price_patterns = [
        (r'rm(\d+\.?\d*)', lambda m: float(m.group(1))),
        (r'(\d+\.\d{2})\s*(?:per\s+nos)?', lambda m: float(m.group(1))),
    ]
    
    found_price = None
    price_end = len(line_clean)
    
    for pattern, converter in price_patterns:
        for m in re.finditer(pattern, line_clean, re.IGNORECASE):
            pos = m.start()
            # Must be at/near end of line (within last 15 chars)
            if len(line_clean) - pos <= 20:
                val = converter(m)
                if val < 50:  # Sanity check: prices should be < RM50/kg
                    found_price = val
                    price_end = pos
                    break
    
    if found_price is None:
        return None
    
    # Extract item number
    item_no = ''
    item_match = re.match(r'\(?(\d+[a-z]?)\)?\s*', line[:price_end])
    if item_match:
        item_no = item_match.group(1)
    
    # Clean up the name text (remove item number, trailing whitespace)
    name_raw = line_clean[:price_end].strip()
    if item_no:
        remaining = line_clean[len(item_match.group(0)):price_end].strip()
        if remaining:
            name_raw = remaining
    
    # Clean up name - remove excess whitespace, normalize separators
    name = re.sub(r'\s+', ' ', name_raw).strip()
    name = name.rstrip('.').rstrip(',').strip()
    
    # Skip if no meaningful name
    if len(name) < 2:
        return None
    
    # Generate display name
    name_lower = name.lower()
    display_name = name  # Default
    
    # Try to map to known product
    for key, cn_name in sorted(PRODUCT_NAMES.items(), key=lambda x: -len(x[0])):
        if key in name_lower:
            # Use the mapped Chinese name but keep some original info
            origin = ''
            if 'import' in name_lower or '*im*' in name_lower:
                origin = '进口'
            elif 'local' in name_lower or '*lo*' in name_lower or '*lo' in name_lower:
                origin = '本地'
            display_name = f'{cn_name}{origin}' if origin else cn_name
            if 'original' in name_lower:
                display_name = f'{cn_name}原装'
            break
    
    return {
        'item': item_no,
        'code': name.split('(')[0].split()[0].upper() if name.split() else '',
        'name': display_name,
        'name_raw': name,
        'price_src': found_price,
        'price_calc': round(found_price / 0.9, 4),
        'price': round_to_10sen(found_price / 0.9),
    }


def parse_prices(text):
    """Parse the full price list text."""
    items = []
    for line in text.split('\n'):
        result = parse_price_line(line)
        if result:
            items.append(result)
    return items


def main():
    if not os.path.exists(RAW_FILE):
        print('⚠️  chan_raw.json not found')
        return
    
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    items = parse_prices(raw.get('text', ''))
    
    if not items:
        print('⚠️  No prices found')
        return
    
    output = {
        'date': raw.get('date', raw.get('updated', '')),
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'source': '冷冻鸡批发价',
        'note': '价格已含/0.9调整，四舍五入至0.10',
        'items': items,
    }
    
    # Curated highlights for restaurant owners - key cuts
    highlight_map = {
        'whole chicken': '全鸡',
        'drumstick': '鸡腿',
        'mid joint wing': '鸡中翅',
        'bb original': '去骨鸡胸肉原装',
        'bb butterfly': '去骨鸡胸肉蝴蝶',
        'thigh import': '鸡大腿肉进口',
        'thigh local': '鸡大腿肉本地',
        'wl jc im': '全鸡腿进口',
        'wl jc lo': '全鸡腿本地',
        'bl im': '去骨鸡腿肉进口',
        'bl lo': '去骨鸡腿肉本地',
        'chop 8': '鸡块8块装',
        'chop 9': '鸡块9块装',
        'fillet': '鸡柳肉',
        'wing import': '鸡翅进口',
        'wing local': '鸡翅本地',
    }
    highlights = []
    seen = set()
    for item in items:
        nl = item['name_raw'].lower()
        for kw, label in highlight_map.items():
            if kw in nl:
                if label not in seen:
                    seen.add(label)
                    entry = dict(item)
                    entry['display'] = label
                    highlights.append(entry)
                break
    if highlights:
        output['highlights'] = highlights
    
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 解析完成: {len(items)} 项, 高亮 {len(highlights)} 项")
    print(f"   输出: {OUT_FILE}")


if __name__ == '__main__':
    main()
