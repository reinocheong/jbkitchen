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

# Abbreviation → readable English mapping
ABBR_MAP = {
    'bb': 'Boneless Breast',
    'sbb': 'Skinless Boneless Breast',
    'bl': 'Boneless Leg',
    'sbl': 'Skinless Boneless Leg',
    'sbL': 'Skinless Boneless Leg',
    'wl': 'Whole Leg',
    'wL': 'Whole Leg',
    'jc': 'JC',
    'im': 'Import',
    'lo': 'Local',
    'sbt': 'Skinless Boneless Thigh',
    'sbL cube': 'Skinless Boneless Leg Cube',
}


def round_to_10sen(val):
    """Round to nearest 0.10 (10 sen). 0.05 → up"""
    return math.floor(val * 10 + 0.5) / 10


def clean_product_name(raw):
    """Clean up product codes to readable English."""
    name = raw.strip()
    
    # Remove leading/trailing punctuation
    name = name.rstrip('.').rstrip(',').strip()
    
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name)
    
    # First check for known multi-word patterns
    name_lower = name.lower()
    
    # Expand abbreviations in order (longest first to avoid partial matches)
    # First handle the BB(boneless breast) pattern - split between code and description
    # Insert space before parentheses
    name = re.sub(r'([a-z])(\()', r'\1 (', name)
    name = re.sub(r'(\))([a-z])', r'\1 \2', name)
    
    tokens = re.split(r'[\s/]+', name)
    expanded = []
    for token in tokens:
        t_lower = token.lower().strip('*()')
        if t_lower in ABBR_MAP:
            expanded.append(ABBR_MAP[t_lower])
        else:
            # Capitalize first letter, keep rest (but preserve ALL CAPS brands)
            if token.isupper() and len(token) > 1:
                expanded.append(token)  # Keep brands like CARGIL, TYSON as-is
            else:
                expanded.append(token.capitalize() if token.islower() or token[0].islower() else token)
    
    name = ' '.join(expanded)
    
    # Clean up *IM*/*LO* etc
    name = re.sub(r'\s*\*\s*([A-Za-z]+)\s*\*', r' \1', name)
    name = re.sub(r'\s*/\s*', '/', name)
    
    # Normalize spaces again
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def parse_price_line(line):
    """Parse a single line from the price list."""
    line = line.strip()
    if not line:
        return None
    
    # Skip non-item lines
    skip_keywords = [
        'delivery', 'self-collect', 'operation hours', 'special discount',
        'puchong food', 'sila hubungi', 'sila hantar', 'for cash term',
        'kindly submit', 'terima kasih', 'thank you', 'half/full',
        'cash term', 'transport discount', 'container', 'please call',
        'no 4,', 'taman perindustrian', 'mon–fri', 'sat :'
    ]
    if any(kw in line.lower() for kw in skip_keywords):
        return None
    
    # Remove size ranges (0.8-0.9), these are weights not prices
    line_clean = re.sub(r'\([\d.]+-[\d.]+\s*(?:kg)?\)', '', line, flags=re.IGNORECASE)
    # Remove multi-dot codes like (11.12.13)
    line_clean = re.sub(r'\([\d.]+\.[\d.]+\)', '', line_clean)
    
    # Find price at/near end of line
    found_price = None
    price_end = len(line_clean)
    
    # Pattern 1: rmX.XX
    m = re.search(r'rm(\d+\.?\d*)', line_clean, re.IGNORECASE)
    if m and len(line_clean) - m.start() <= 25:
        val = float(m.group(1))
        if val < 50:
            found_price = val
            price_end = m.start()
    
    # Pattern 2: X.XX at end (with or without "per nos")
    if found_price is None:
        m = re.search(r'(\d+\.\d{2})\s*(?:per\s+nos)?', line_clean, re.IGNORECASE)
        if m and len(line_clean) - m.start() <= 20:
            val = float(m.group(1))
            if val < 50:
                found_price = val
                price_end = m.start()
    
    if found_price is None:
        return None
    
    # Extract item number
    item_no = ''
    item_match = re.match(r'\(?(\d+[a-z]?)\)?\s*', line_clean[:price_end])
    if item_match:
        item_no = item_match.group(1)
    
    # Extract name (after item number, before price)
    name_raw = line_clean[:price_end].strip()
    if item_no:
        remaining = line_clean[len(item_match.group(0)):price_end].strip()
        if remaining:
            name_raw = remaining
    name_raw = re.sub(r'\s+', ' ', name_raw).strip()
    name_raw = name_raw.rstrip('.').rstrip(',').strip()
    
    if len(name_raw) < 2:
        return None
    
    # Clean up product name
    display_name = clean_product_name(name_raw)
    
    # Derive product code
    code = ''
    code_match = re.match(r'([A-Za-z]+)', name_raw.strip())
    if code_match:
        code_base = code_match.group(1).upper()
        # Special handling for known codes
        if code_base == 'BB':
            code = 'BB'
        elif code_base == 'SBB':
            code = 'SBB'
        elif code_base in ('BL',):
            code = 'BL'
        elif code_base in ('WL', 'WL'):
            code = 'WL'
        elif code_base == 'SBL':
            code = 'SBL'
        else:
            code = code_base
    
    return {
        'item': item_no,
        'code': code,
        'name': display_name,
        'name_raw': name_raw,
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
        'source': 'Frozen Chicken Wholesale Price',
        'note': 'Price = source / 0.9, rounded to nearest RM0.10',
        'items': items,
    }
    
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 解析完成: {len(items)} 项")
    print(f"   输出: {OUT_FILE}")


if __name__ == '__main__':
    main()
