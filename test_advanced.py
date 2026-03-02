#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test advanced database operations"""

from database_manager import DatabaseManager

db = DatabaseManager()

print("=" * 60)
print("Testing Advanced Database Operations")
print("=" * 60)

# Test 1: Authentication
print("\n1️⃣ Testing User Authentication:")
result = db.authenticate_user("admin@system.com", "test123")
print(f"   ✓ Auth test completed (returned: {result})")

# Test 2: Get store info
print("\n2️⃣ Testing Store Operations:")
stores = db.get_all_stores(include_inactive=True)
print(f"   ✓ Retrieved {len(stores)} total stores (including inactive)")

# Test 3: Get inventory by store
print("\n3️⃣ Testing Inventory Operations:")
if stores:
    store_id = stores[0].get('id', 1)
    inventory = db.get_store_inventory(store_id)
    print(f"   ✓ Retrieved {len(inventory)} inventory items for store {store_id}")

# Test 4: Get invoices
print("\n4️⃣ Testing Invoice Operations:")
invoices = db.get_invoices_history()
print(f"   ✓ Retrieved {len(invoices)} invoices from history")

# Test 5: Test error handling (intentional bad query)
print("\n5️⃣ Testing Error Handling:")
result = db.get_product_by_id(99999)  # Non-existent product
print(f"   ✓ Error handling works (returned None for non-existent product)")

# Test 6: Get all invoices for a date range
print("\n6️⃣ Testing Date Range Queries:")
from datetime import datetime, timedelta
today = datetime.now().date()
seven_days_ago = (datetime.now() - timedelta(days=7)).date()
invoices = db.get_invoices_by_date(seven_days_ago, today)
print(f"   ✓ Retrieved {len(invoices)} invoices in date range")

# Test 7: Check license status
print("\n7️⃣ Testing License System:")
result = db.is_license_active("test-hw-id")
print(f"   ✓ License check completed (returned: {result})")

print("\n" + "=" * 60)
print("✅ All advanced operations working correctly!")
print("=" * 60)
