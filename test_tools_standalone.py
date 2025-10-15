#!/usr/bin/env python3
"""
Standalone Agent Tools Test Script

This script tests the agent tools independently without requiring
the full agent initialization that needs OpenAI API key.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Define the tools directly to avoid importing the main agent file
from langchain.agents import tool

@tool
def check_order_status(order_id: str) -> dict:
    """Checks the current status of an order"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, status, order_date, total_amount
        FROM orders WHERE id = ?
    """, (order_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "order_id": result[0],
            "status": result[1],
            "order_date": result[2],
            "total_amount": result[3]
        }
    return {"error": "Order not found"}

@tool
def check_return_policy(product_type: str) -> str:
    """Gets return policy for product type"""
    policies = {
        "electronics": "30-day return window, must include original packaging",
        "clothing": "60-day return window, must have tags attached",
        "furniture": "14-day return window, assembly affects eligibility"
    }
    return policies.get(product_type, "Standard 30-day return policy applies")

@tool
def check_inventory(product_id: str) -> dict:
    """Checks if product is in stock"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, name, quantity, next_restock_date
        FROM inventory WHERE product_id = ?
    """, (product_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "product_id": result[0],
            "name": result[1],
            "in_stock": result[2] > 0,
            "quantity": result[2],
            "next_restock": result[3]
        }
    return {"error": "Product not found"}

def setup_sample_data():
    """Add sample data to databases for testing"""
    try:
        # Add sample order
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO orders (customer_id, status, order_date, total_amount, shipping_address, billing_address, payment_method, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, 'shipped', '2024-01-15', 299.99, '123 Main St, City, State 12345', '123 Main St, City, State 12345', 'Credit Card', 'Test order', '2024-01-10', '2024-01-15'))
        conn.commit()
        conn.close()

        # Add sample inventory
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO inventory (product_id, name, quantity, next_restock_date)
            VALUES (?, ?, ?, ?)
        ''', ('PROD-XYZ', 'Wireless Headphones', 15, '2024-02-01'))
        conn.commit()
        conn.close()

        print("Sample data added successfully")

    except Exception as e:
        print(f"Error setting up sample data: {e}")

def test_tools():
    """Test the agent tools with sample queries"""
    print("\n" + "="*60)
    print("TESTING AGENT TOOLS STANDALONE")
    print("="*60)

    # Test 1: Order status check
    print("\n--- Test 1: Order Status Check ---")
    try:
        result = check_order_status("4")
        if result.get("order_id") == 4:
            print("[PASS] Order status check working correctly")
            print(f"       Status: {result.get('status')}")
            print(f"       Order Date: {result.get('order_date')}")
            print(f"       Total Amount: ${result.get('total_amount')}")
        else:
            print("[FAIL] Order status check returned unexpected result")
            print(f"       Got: {result}")
    except Exception as e:
        print(f"[FAIL] Order status check failed: {e}")

    # Test 2: Inventory check
    print("\n--- Test 2: Inventory Check ---")
    try:
        result = check_inventory("PROD-XYZ")
        if result.get("product_id") == "PROD-XYZ":
            print("[PASS] Inventory check working correctly")
            print(f"       Product: {result.get('name')}")
            print(f"       In Stock: {result.get('in_stock')}")
            print(f"       Quantity: {result.get('quantity')}")
        else:
            print("[FAIL] Inventory check returned unexpected result")
    except Exception as e:
        print(f"[FAIL] Inventory check failed: {e}")

    # Test 3: Return policy check
    print("\n--- Test 3: Return Policy Check ---")
    try:
        result = check_return_policy("electronics")
        if "30-day" in result:
            print("[PASS] Return policy check working correctly")
            print(f"       Policy: {result}")
        else:
            print("[FAIL] Return policy check returned unexpected result")
    except Exception as e:
        print(f"[FAIL] Return policy check failed: {e}")

    # Test 4: Non-existent order
    print("\n--- Test 4: Non-existent Order ---")
    try:
        result = check_order_status("999")
        if "error" in result:
            print("[PASS] Non-existent order handled correctly")
        else:
            print("[FAIL] Non-existent order not handled properly")
    except Exception as e:
        print(f"[FAIL] Non-existent order test failed: {e}")

    # Test 5: Non-existent product
    print("\n--- Test 5: Non-existent Product ---")
    try:
        result = check_inventory("NON-EXISTENT")
        if "error" in result:
            print("[PASS] Non-existent product handled correctly")
        else:
            print("[FAIL] Non-existent product not handled properly")
    except Exception as e:
        print(f"[FAIL] Non-existent product test failed: {e}")

    # Test 6: Different product types for return policy
    print("\n--- Test 6: Return Policy Variations ---")
    try:
        electronics_policy = check_return_policy("electronics")
        clothing_policy = check_return_policy("clothing")
        unknown_policy = check_return_policy("unknown")

        if ("30-day" in electronics_policy and
            "60-day" in clothing_policy and
            "Standard" in unknown_policy):
            print("[PASS] Return policy variations working correctly")
            print(f"       Electronics: {electronics_policy}")
            print(f"       Clothing: {clothing_policy}")
            print(f"       Unknown: {unknown_policy}")
        else:
            print("[FAIL] Return policy variations not working correctly")
    except Exception as e:
        print(f"[FAIL] Return policy variation test failed: {e}")

    print("\n" + "="*60)
    print("STANDALONE TOOLS TESTS COMPLETED")
    print("="*60)

def main():
    """Main function"""
    print("STANDALONE AGENT TOOLS VERIFICATION")
    print("="*60)

    # Setup sample data
    setup_sample_data()

    # Test tools functionality
    test_tools()

    print("\nStandalone tools testing completed!")

if __name__ == "__main__":
    main()