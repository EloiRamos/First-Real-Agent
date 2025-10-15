#!/usr/bin/env python3
"""
Comprehensive Agent Installation Test Script

This script tests all aspects of the agent installation including:
1. Import verification for all dependencies
2. Database accessibility and structure validation
3. Basic agent functionality testing
4. Virtual environment verification
5. Performance metrics collection

Run this script to verify your agent installation is working correctly.
"""

import sys
import os
import subprocess
import sqlite3
import importlib
import time
from datetime import datetime
import traceback

class AgentInstallationTester:
    def __init__(self):
        self.test_results = {
            "imports": [],
            "databases": [],
            "agent_functionality": [],
            "environment": [],
            "overall": {"passed": 0, "failed": 0, "total": 0}
        }
        self.start_time = time.time()

    def log_test(self, category, test_name, status, message, error=None):
        """Log a test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        self.test_results[category].append(result)
        self.test_results["overall"]["total"] += 1

        if status == "PASS":
            self.test_results["overall"]["passed"] += 1
            print(f"[PASS] {test_name}: {message}")
        else:
            self.test_results["overall"]["failed"] += 1
            print(f"[FAIL] {test_name}: {message}")
            if error:
                print(f"   Error: {error}")

    def test_imports(self):
        """Test all required imports"""
        print("\n" + "="*60)
        print("TESTING IMPORTS")
        print("="*60)

        # Core Python imports
        core_imports = [
            ("sqlite3", "sqlite3", "Standard library database module"),
            ("datetime", "datetime", "Standard library datetime module"),
            ("sys", "sys", "Standard library system module"),
            ("os", "os", "Standard library OS module"),
            ("logging", "logging", "Standard library logging module")
        ]

        for module_name, import_name, description in core_imports:
            try:
                module = __import__(import_name)
                self.log_test("imports", f"Import {module_name}", "PASS",
                            f"Successfully imported {description}")
            except ImportError as e:
                self.log_test("imports", f"Import {module_name}", "FAIL",
                            f"Failed to import {description}", str(e))

        # Third-party imports
        third_party_imports = [
            ("langchain.agents", "langchain.agents", "LangChain agents framework"),
            ("langchain.agents.tool", "langchain.agents", "LangChain tool decorator"),
            ("langchain_openai", "langchain_openai", "LangChain OpenAI integration"),
            ("langchain.prompts", "langchain.prompts", "LangChain prompts"),
            ("langchain.agents.AgentExecutor", "langchain.agents", "Agent executor"),
            ("langchain.agents.create_openai_tools_agent", "langchain.agents", "OpenAI tools agent"),
            ("langchain.prompts.ChatPromptTemplate", "langchain.prompts", "Chat prompt template"),
            ("langchain.prompts.MessagesPlaceholder", "langchain.prompts", "Messages placeholder")
        ]

        for module_name, import_name, description in third_party_imports:
            try:
                module = __import__(import_name, fromlist=[''])
                self.log_test("imports", f"Import {module_name}", "PASS",
                            f"Successfully imported {description}")
            except ImportError as e:
                self.log_test("imports", f"Import {module_name}", "FAIL",
                            f"Failed to import {description}", str(e))

    def test_databases(self):
        """Test database accessibility and structure"""
        print("\n" + "="*60)
        print("TESTING DATABASES")
        print("="*60)

        databases = [
            ("orders.db", "orders"),
            ("inventory.db", "inventory"),
            ("tickets.db", "tickets")
        ]

        for db_file, table_name in databases:
            # Test database file accessibility
            if os.path.exists(db_file):
                self.log_test("databases", f"Database file {db_file}", "PASS",
                            f"Database file exists and is accessible")

                # Test database connection and structure
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()

                    # Check if table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if cursor.fetchone():
                        self.log_test("databases", f"Table {table_name} in {db_file}", "PASS",
                                    f"Table {table_name} exists in database")

                        # Get table structure
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                        self.log_test("databases", f"Table structure {table_name}", "PASS",
                                    f"Table has columns: {', '.join(column_names)}")

                        # Test sample query
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        self.log_test("databases", f"Query test {table_name}", "PASS",
                                    f"Successfully queried {table_name} table (found {count} records)")

                    else:
                        self.log_test("databases", f"Table {table_name} in {db_file}", "FAIL",
                                    f"Table {table_name} does not exist in database")

                    conn.close()

                except sqlite3.Error as e:
                    self.log_test("databases", f"Database connection {db_file}", "FAIL",
                                f"Failed to connect to or query database", str(e))

            else:
                self.log_test("databases", f"Database file {db_file}", "FAIL",
                            f"Database file does not exist or is not accessible")

    def test_virtual_environment(self):
        """Test virtual environment activation"""
        print("\n" + "="*60)
        print("TESTING VIRTUAL ENVIRONMENT")
        print("="*60)

        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

        if in_venv:
            self.log_test("environment", "Virtual Environment Detection", "PASS",
                        "Running within a virtual environment")
            self.log_test("environment", "Virtual Environment Path", "PASS",
                        f"Virtual environment located at: {sys.prefix}")
        else:
            self.log_test("environment", "Virtual Environment Detection", "WARN",
                        "Not running within a virtual environment (may be using system Python)")

        # Check Python path
        self.log_test("environment", "Python Executable", "PASS",
                    f"Using Python executable: {sys.executable}")

        # Check Python version
        self.log_test("environment", "Python Version", "PASS",
                    f"Python version: {sys.version}")

        # Check current working directory
        self.log_test("environment", "Working Directory", "PASS",
                    f"Current working directory: {os.getcwd()}")

        # Check if .env file exists
        if os.path.exists('.env'):
            self.log_test("environment", ".env File", "PASS",
                        ".env file exists for configuration")
        else:
            self.log_test("environment", ".env File", "WARN",
                        ".env file not found (may need manual configuration)")

    def test_agent_functionality(self):
        """Test basic agent functionality"""
        print("\n" + "="*60)
        print("TESTING AGENT FUNCTIONALITY")
        print("="*60)

        try:
            # Import agent components
            from langchain.agents import tool
            from langchain_openai import ChatOpenAI
            from langchain.agents import AgentExecutor, create_openai_tools_agent
            from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

            self.log_test("agent_functionality", "Agent Component Imports", "PASS",
                        "Successfully imported all agent components")

            # Test tool creation
            @tool
            def test_tool(test_param: str) -> str:
                """Test tool for functionality verification"""
                return f"Test tool executed with parameter: {test_param}"

            self.log_test("agent_functionality", "Tool Creation", "PASS",
                        "Successfully created test tool")

            # Test tool execution
            result = test_tool.run({"test_param": "test_value"})
            if "test_value" in result:
                self.log_test("agent_functionality", "Tool Execution", "PASS",
                            "Test tool executed successfully")
            else:
                self.log_test("agent_functionality", "Tool Execution", "FAIL",
                            "Test tool execution failed or returned unexpected result")

            # Test database tool functions (without full agent setup)
            try:
                # Test order status check
                conn = sqlite3.connect('orders.db')
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM orders')
                count = cursor.fetchone()[0]
                conn.close()

                self.log_test("agent_functionality", "Database Tool Access", "PASS",
                            f"Database tools can access orders table ({count} records found)")

            except Exception as e:
                self.log_test("agent_functionality", "Database Tool Access", "FAIL",
                            "Database tools cannot access required tables", str(e))

        except ImportError as e:
            self.log_test("agent_functionality", "Agent Component Imports", "FAIL",
                        "Failed to import agent components", str(e))
        except Exception as e:
            self.log_test("agent_functionality", "Agent Functionality", "FAIL",
                        "Unexpected error during agent functionality test", str(e))

    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("AGENT INSTALLATION TEST SUITE")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all test categories
        self.test_imports()
        self.test_databases()
        self.test_virtual_environment()
        self.test_agent_functionality()

        # Calculate total time
        total_time = time.time() - self.start_time

        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        print(f"Total Tests: {self.test_results['overall']['total']}")
        print(f"Passed: {self.test_results['overall']['passed']}")
        print(f"Failed: {self.test_results['overall']['failed']}")
        print(f"Total Time: {total_time:.2f} seconds")

        # Calculate success rate
        if self.test_results['overall']['total'] > 0:
            success_rate = (self.test_results['overall']['passed'] / self.test_results['overall']['total']) * 100
            print(f"Success Rate: {success_rate:.1f}%")

            if success_rate == 100:
                print("\n[SUCCESS] ALL TESTS PASSED! Agent installation is working correctly.")
            elif success_rate >= 80:
                print("\n[WARNING] MOST TESTS PASSED! Agent installation is mostly working.")
                print("   Check failed tests for minor issues.")
            else:
                print("\n[ERROR] SEVERAL TESTS FAILED! Agent installation needs attention.")
                print("   Review failed tests and fix issues before proceeding.")
        else:
            print("No tests were executed.")
    
            # Show failed tests if any
            if self.test_results['overall']['failed'] > 0:
                print("\n[FAILED TESTS]:")
            for category, tests in self.test_results.items():
                if category != "overall":
                    for test in tests:
                        if test['status'] == "FAIL":
                            print(f"  - {test['test_name']}: {test['message']}")

        return self.test_results

def main():
    """Main function to run the test suite"""
    tester = AgentInstallationTester()
    results = tester.run_all_tests()

    # Return appropriate exit code
    if results['overall']['failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some failures

if __name__ == "__main__":
    main()