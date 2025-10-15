#!/usr/bin/env python3
"""
Agent Functionality Test Script

This script tests the actual agent functionality with sample queries
to verify that the agent can process customer requests correctly.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add sample data to databases for testing
def setup_sample_data():
    """Add sample data to databases for testing"""
    try:
        # Add sample order
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO orders (customer_id, status, order_date, total_amount)
            VALUES (?, ?, ?, ?)
        ''', (1, 'shipped', '2024-01-15', 299.99))
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

def test_agent_with_sample_queries():
    """Test the agent with sample customer queries"""
    print("\n" + "="*60)
    print("TESTING AGENT TOOLS WITH SAMPLE QUERIES")
    print("="*60)

    # Import the agent tools directly (without full agent initialization)
    try:
        from first_real_agent import check_order_status, check_inventory, check_return_policy

        print("Agent tools imported successfully")

        # Test 1: Order status check
        print("\n--- Test 1: Order Status Check ---")
        try:
            result = check_order_status("1")
            if result.get("order_id") == 1:
                print("[PASS] Order status check working correctly")
                print(f"       Status: {result.get('status')}")
                print(f"       Order Date: {result.get('order_date')}")
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

        print("\n" + "="*60)
        print("AGENT TOOLS TESTS COMPLETED")
        print("="*60)

    except ImportError as e:
        print(f"[FAIL] Could not import agent tools: {e}")
    except Exception as e:
        print(f"[FAIL] Unexpected error during agent testing: {e}")

def main():
    """Main function"""
    print("AGENT FUNCTIONALITY VERIFICATION")
    print("="*60)

    # Setup sample data
    setup_sample_data()

    # Test agent functionality
    test_agent_with_sample_queries()

    print("\nAgent functionality testing completed!")

if __name__ == "__main__":
    main()