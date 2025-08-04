#!/usr/bin/env python3
"""
Test script to verify the project setup is working correctly.
Run this after setting up the virtual environment and installing dependencies.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("=== Testing Package Imports ===")
    
    try:
        import pyodbc
        print("✓ pyodbc imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pyodbc: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SQLAlchemy: {e}")
        return False
    
    try:
        import dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dotenv: {e}")
        return False
    
    return True


def test_project_structure():
    """Test that the project structure is correct."""
    print("\n=== Testing Project Structure ===")
    
    required_dirs = ['src', 'db', 'data', 'scripts', 'Docker']
    required_files = [
        'requirements.txt',
        'env.example',
        'README.md',
        'src/database.py',
        'db/init_schema.py',
        'db/load_csv.py',
        'scripts/run_sqlserver.sh',
        'Docker/docker-compose.yml'
    ]
    
    all_good = True
    
    # Check directories
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory '{dir_name}' exists")
        else:
            print(f"✗ Directory '{dir_name}' missing")
            all_good = False
    
    # Check files
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ File '{file_name}' exists")
        else:
            print(f"✗ File '{file_name}' missing")
            all_good = False
    
    return all_good


def test_odbc_drivers():
    """Test ODBC driver detection."""
    print("\n=== Testing ODBC Drivers ===")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_server_drivers:
            print("✓ SQL Server ODBC drivers found:")
            for driver in sql_server_drivers:
                print(f"  - {driver}")
        else:
            print("⚠ No SQL Server ODBC drivers found")
            print("  You may need to install Microsoft ODBC Driver 18 for SQL Server")
            print("  On macOS: brew install msodbcsql18")
        
        return True
    except Exception as e:
        print(f"✗ Error checking ODBC drivers: {e}")
        return False


def test_environment_setup():
    """Test environment configuration."""
    print("\n=== Testing Environment Setup ===")
    
    # Check if .env exists
    if Path('.env').exists():
        print("✓ .env file exists")
    else:
        print("⚠ .env file not found")
        print("  Copy env.example to .env and configure your settings")
    
    # Check if env.example exists
    if Path('env.example').exists():
        print("✓ env.example file exists")
    else:
        print("✗ env.example file missing")
        return False
    
    return True


def test_script_permissions():
    """Test that scripts have proper permissions."""
    print("\n=== Testing Script Permissions ===")
    
    script_path = Path('scripts/run_sqlserver.sh')
    if script_path.exists():
        if os.access(script_path, os.X_OK):
            print("✓ run_sqlserver.sh is executable")
        else:
            print("⚠ run_sqlserver.sh is not executable")
            print("  Run: chmod +x scripts/run_sqlserver.sh")
    else:
        print("✗ run_sqlserver.sh not found")
        return False
    
    return True


def main():
    """Run all tests."""
    print("SQL Server Python Project - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_project_structure,
        test_odbc_drivers,
        test_environment_setup,
        test_script_permissions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and configure settings")
        print("2. Start SQL Server: ./scripts/run_sqlserver.sh start")
        print("3. Test connection: python src/database.py")
        print("4. Initialize schema: python db/init_schema.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 