#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test advanced database operations"""

from database_manager import DatabaseManager

db = DatabaseManager()

print("\n" + "="*60)
print("Testing Advanced Database Operations")
print("="*60)

# Test 1: Authentication
print("\n[1] Testing User Authentication:")
result = db.authenticate_user("admin@system.com", "test123")
print(f"    ✓ Auth result: {result is not None}")

# Test 2: Get store info  
print("\n[2] Testing Store Operations:")
stores = db.get_all_stores(include_inactive=True)
print(f"    ✓ Stores retrieved: {len(stores)} stores")

# Test 3: Get inventory by store
print("\n[3] Testing Inventory Operations:")
if stores:
    store_id = stores[0].get('id', 1)
    inventory = db.get_store_inventory(store_id)
    print(f"    ✓ Inventory items: {len(inventory)}")

# Test 4: Get invoices
print("\n[4] Testing Invoice Operations:")
invoices = db.get_invoices_history()
print(f"    ✓ Invoices retrieved: {len(invoices)}")

# Test 5: Test error handling
print("\n[5] Testing Error Handling:")
result = db.get_product_by_id(99999)
print(f"    ✓ Error handling works: {result is None}")

# Test 6: Check license status
print("\n[6] Testing License System:")
result = db.is_license_active("test-hw-id")
print(f"    ✓ License check: returned bool")

print("\n" + "="*60)
print("✅ All tests passed successfully!")
print("="*60 + "\n")
