#!/usr/bin/env python3
"""
Database schema initialization script.
Creates the products table and other necessary database objects.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from database import SQLServerConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_products_table():
    """Create the products table with sample schema."""
    
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='products' AND xtype='U')
    CREATE TABLE products (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        description NVARCHAR(MAX),
        price DECIMAL(10,2) NOT NULL,
        category NVARCHAR(100),
        stock_quantity INT DEFAULT 0,
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE()
    )
    """
    
    create_index_sql = """
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_products_category')
    CREATE INDEX IX_products_category ON products(category)
    """
    
    try:
        conn_manager = SQLServerConnection()
        
        # Test connection first
        if not conn_manager.test_pyodbc_connection():
            logger.error("Cannot connect to database. Please check your connection settings.")
            return False
        
        # Create table
        logger.info("Creating products table...")
        conn_manager.execute_query_pyodbc(create_table_sql)
        
        # Create index
        logger.info("Creating index on category column...")
        conn_manager.execute_query_pyodbc(create_index_sql)
        
        logger.info("✓ Products table created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create products table: {e}")
        return False


def create_sample_data():
    """Insert sample data into the products table."""
    
    sample_data_sql = """
    IF NOT EXISTS (SELECT * FROM products WHERE name = 'Sample Product 1')
    INSERT INTO products (name, description, price, category, stock_quantity) VALUES
    ('Sample Product 1', 'This is a sample product for testing', 29.99, 'Electronics', 100),
    ('Sample Product 2', 'Another sample product', 49.99, 'Electronics', 50),
    ('Sample Product 3', 'A third sample product', 19.99, 'Books', 200),
    ('Sample Product 4', 'Yet another sample', 99.99, 'Home & Garden', 25),
    ('Sample Product 5', 'The last sample product', 15.99, 'Books', 150)
    """
    
    try:
        conn_manager = SQLServerConnection()
        
        logger.info("Inserting sample data...")
        conn_manager.execute_query_pyodbc(sample_data_sql)
        
        logger.info("✓ Sample data inserted successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        return False


def verify_schema():
    """Verify that the schema was created correctly."""
    
    verify_sql = """
    SELECT 
        COUNT(*) as total_products,
        AVG(price) as avg_price,
        SUM(stock_quantity) as total_stock
    FROM products
    """
    
    try:
        conn_manager = SQLServerConnection()
        
        logger.info("Verifying schema...")
        result = conn_manager.execute_query_pyodbc(verify_sql)
        
        if not result.empty:
            row = result.iloc[0]
            logger.info(f"✓ Schema verification successful!")
            logger.info(f"  - Total products: {row['total_products']}")
            logger.info(f"  - Average price: ${row['avg_price']:.2f}")
            logger.info(f"  - Total stock: {row['total_stock']}")
            return True
        else:
            logger.warning("No data found in products table")
            return False
            
    except Exception as e:
        logger.error(f"Failed to verify schema: {e}")
        return False


def main():
    """Main function to initialize the database schema."""
    
    print("=== Database Schema Initialization ===")
    print()
    
    # Create products table
    if create_products_table():
        print("✓ Products table created")
    else:
        print("✗ Failed to create products table")
        return False
    
    # Insert sample data
    if create_sample_data():
        print("✓ Sample data inserted")
    else:
        print("✗ Failed to insert sample data")
        return False
    
    # Verify schema
    if verify_schema():
        print("✓ Schema verification passed")
    else:
        print("✗ Schema verification failed")
        return False
    
    print()
    print("=== Schema initialization completed successfully! ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 