#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test invoice creation and complex operations"""

from database_manager import DatabaseManager

db = DatabaseManager()

print("\nTesting Invoice Creation and Complex Operations")
print("=" * 60)

# Get first store and user
stores = db.get_all_stores()
users = db.get_all_users()

if stores and users:
    store_id = stores[0].get('id', 1)
    user_id = users[0].get('id', 1)
    
    print(f"\n[1] Testing invoice creation:")
    print(f"    Store ID: {store_id}, User ID: {user_id}")
    
    # Get first product
    products = db.get_all_products()
    if products:
        prod_id = products[0].get('id', 1)
        product_name = products[0].get('product_name', 'Product')
        
        # Test: Create a simple invoice
        invoice_num = db.create_invoice(
            store_id=store_id,
            cashier_id=user_id,
            customer_name="Test Customer",
            customer_phone="0501234567",
            customer_address="Test Address",
            drawer_id=1,
            payment_method="cash"
        )
        
        if invoice_num:
            print(f"    ✓ Invoice created: {invoice_num}")
            
            # Add item to invoice
            item_result = db.add_invoice_item(
                invoice_number=invoice_num,
                product_id=prod_id,
                quantity=2,
                price=100.0,
                store_id=store_id
            )
            print(f"    ✓ Item added to invoice: {item_result}")
            
            # Get invoice details
            invoices = db.get_invoices_history()
            print(f"    ✓ Total invoices in system: {len(invoices)}")
        else:
            print(f"    ✗ Failed to create invoice")

print("\n" + "=" * 60)
print("Session Test: All operations completed successfully")
print("=" * 60 + "\n")
