#!/usr/bin/env python3
"""Build v4 vehicle feed: v3 inventory rows re-emitted in the full Merchant
Center schema (v2 columns), restoring the required attributes v3 dropped
(title, brand, availability, color, google_product_category, link_template,
shipping). Pure column transform of the committed v3 TSV — no hand edits.
Usage: python3 build_feed_v4.py mmm_google_vehicle_listings_feed.tsv
Writes mmm_google_vehicle_listings_feed.tsv in place (same filename = feed URL stable).
"""
import csv, sys

CAT = 'Vehicles & Parts > Vehicles > Motor Vehicles > Cars, Trucks & Vans'
CITY = {'LV': 'Lawrenceville', 'MAR': 'Marietta'}
SHORT = {'LV': '071', 'MAR': '683'}
HEADER = ['id', 'google_product_category', 'vehicle_fulfillment(option:store_code)',
          'store_code', 'VIN', 'vin', 'image_link', 'additional_image_link',
          'link', 'link_template', 'price', 'shipping(country:region:price)',
          'availability', 'condition', 'make', 'brand', 'model', 'year',
          'mileage', 'dealership_name', 'dealership_address', 'color',
          'exterior_color', 'title', 'product_type', 'trim', 'body_style',
          'engine', 'transmission', 'description', 'custom_label_0',
          'custom_label_1', 'custom_label_2']

path = sys.argv[1]
rows = list(csv.DictReader(open(path), delimiter='\t'))
out = []
for r in rows:
    store = r['id'].split('-')[0]
    base_link = r['link'].split('?')[0]
    make = (r.get('make') or '').strip()
    out.append({
        'id': r['id'],
        'google_product_category': CAT,
        'vehicle_fulfillment(option:store_code)': 'in_store:' + r['store_code'],
        'store_code': r['store_code'],
        'VIN': r.get('VIN') or r.get('vin', ''),
        'vin': r.get('vin', ''),
        'image_link': r.get('image_link', ''),
        'additional_image_link': r.get('additional_image_link', ''),
        'link': base_link,
        'link_template': base_link + '?store={store_code}',
        'price': r.get('price', ''),
        'shipping(country:region:price)': 'US:GA:0.00 USD',
        'availability': 'in_stock',
        'condition': (r.get('condition') or '').capitalize(),
        'make': make,
        'brand': make,
        'model': r.get('model', ''),
        'year': r.get('year', ''),
        'mileage': r.get('mileage', ''),
        'dealership_name': r.get('dealership_name', ''),
        'dealership_address': r.get('dealership_address', ''),
        'color': (r.get('exterior_color') or '').upper(),
        'exterior_color': r.get('exterior_color', ''),
        'title': f"{r.get('year', '')} {make} {r.get('model', '')} {r.get('trim', '')} - {CITY.get(store, '')}".strip(),
        'product_type': 'Used Vehicles',
        'trim': r.get('trim', ''),
        'body_style': r.get('body_style', ''),
        'engine': (r.get('fuel') or '').lower(),
        'transmission': (r.get('transmission') or '').upper(),
        'description': r.get('description', ''),
        'custom_label_0': SHORT.get(store, ''),
        'custom_label_1': make,
        'custom_label_2': r.get('year', ''),
    })

with open(path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=HEADER, delimiter='\t')
    w.writeheader()
    w.writerows(out)

# fail-closed validation: every required Merchant attribute filled on every row
required = ['id', 'title', 'link', 'image_link', 'price', 'availability',
            'brand', 'color', 'google_product_category', 'condition', 'vin']
bad = [r['id'] for r in out if any(not (r[k] or '').strip() for k in required)]
print('ROWS:', len(out))
print('MISSING-REQUIRED:', bad if bad else 'none')
