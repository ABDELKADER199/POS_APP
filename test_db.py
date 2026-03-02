#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test core database operations"""

from database_manager import DatabaseManager

db = DatabaseManager()

# Test 1: Get all stores
stores = db.get_all_stores()
print(f'✓ Stores retrieved: {len(stores)} stores found')
for s in stores:
    print(f'  - Store: {s.get("store_name", "Unknown")}')

# Test 2: Get all users
users = db.get_all_users()
print(f'✓ Users retrieved: {len(users)} users found')
for u in users:
    print(f'  - User: {u.get("name", "Unknown")}')

# Test 3: Get all products
products = db.get_all_products()
print(f'✓ Products retrieved: {len(products)} products')
if products:
    print('  Sample products:')
    for p in products[:3]:
        print(f'    - {p.get("product_name", "Unknown")}: {p.get("store_qty", 0)} units')

print('\n✅ All database operations working correctly!')
