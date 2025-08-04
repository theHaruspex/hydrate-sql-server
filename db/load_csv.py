#!/usr/bin/env python3
"""
CSV data loading script.
Reads CSV files from the data directory and loads them into SQL Server tables.
"""

import sys
import os
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from database import SQLServerConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_csv_files():
    """Get list of CSV files in the data directory."""
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        logger.warning(f"Data directory {data_dir} does not exist. Creating it...")
        data_dir.mkdir(parents=True, exist_ok=True)
        return []
    
    csv_files = list(data_dir.glob('*.csv'))
    logger.info(f"Found {len(csv_files)} CSV files in {data_dir}")
    return csv_files


def load_csv_to_products(csv_file):
    """Load CSV data into the products table."""
    
    try:
        # Read CSV file
        logger.info(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)
        
        # Display basic info about the data
        logger.info(f"CSV contains {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Clean and prepare data
        df = prepare_products_data(df)
        
        if df.empty:
            logger.warning("No valid data to insert after cleaning")
            return False
        
        # Load data into SQL Server using pyodbc for better reliability
        conn_manager = SQLServerConnection()
        
        # Check if table exists, if not create it
        create_table_if_not_exists(conn_manager)
        
        # Insert data using pyodbc for better performance
        logger.info(f"Inserting {len(df)} rows into products table...")
        
        # Get connection
        conn = conn_manager.get_pyodbc_connection()
        cursor = conn.cursor()
        
        # Prepare insert statement
        insert_sql = """
        INSERT INTO products (name, description, price, category, stock_quantity, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Insert rows
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                row['name'],
                row['description'],
                row['price'],
                row['category'],
                row['stock_quantity'],
                row['created_at'],
                row['updated_at']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Successfully loaded {len(df)} rows from {csv_file.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load {csv_file}: {e}")
        return False


def prepare_products_data(df):
    """Prepare and clean the DataFrame for products table."""
    
    # Map common column names to our schema
    column_mapping = {
        'name': ['name', 'product_name', 'title', 'product'],
        'description': ['description', 'desc', 'product_description'],
        'price': ['price', 'cost', 'amount', 'value'],
        'category': ['category', 'cat', 'type', 'product_category'],
        'stock_quantity': ['stock_quantity', 'stock', 'quantity', 'qty', 'inventory']
    }
    
    # Try to map columns
    mapped_df = pd.DataFrame()
    
    for target_col, possible_names in column_mapping.items():
        for col_name in possible_names:
            if col_name in df.columns:
                mapped_df[target_col] = df[col_name]
                break
        else:
            # If no matching column found, create empty column
            if target_col == 'price':
                mapped_df[target_col] = 0.0
            elif target_col == 'stock_quantity':
                mapped_df[target_col] = 0
            else:
                mapped_df[target_col] = ''
    
    # Clean data
    if 'price' in mapped_df.columns:
        # Convert price to numeric, handle errors
        mapped_df['price'] = pd.to_numeric(mapped_df['price'], errors='coerce').fillna(0.0)
    
    if 'stock_quantity' in mapped_df.columns:
        # Convert stock to integer, handle errors
        mapped_df['stock_quantity'] = pd.to_numeric(mapped_df['stock_quantity'], errors='coerce').fillna(0).astype(int)
    
    # Ensure required columns exist
    if 'name' not in mapped_df.columns or mapped_df['name'].isna().all():
        logger.error("No valid product name column found in CSV")
        return pd.DataFrame()
    
    # Remove rows with empty names
    mapped_df = mapped_df.dropna(subset=['name'])
    
    # Add timestamp columns
    mapped_df['created_at'] = datetime.now()
    mapped_df['updated_at'] = datetime.now()
    
    logger.info(f"Prepared {len(mapped_df)} valid rows for insertion")
    return mapped_df


def create_table_if_not_exists(conn_manager):
    """Create products table if it doesn't exist."""
    
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
    
    try:
        conn_manager.execute_query_pyodbc(create_table_sql)
        logger.info("Products table created (if it didn't exist)")
    except Exception as e:
        logger.error(f"Failed to create products table: {e}")
        raise


def load_all_csv_files():
    """Load all CSV files in the data directory."""
    
    csv_files = get_csv_files()
    
    if not csv_files:
        logger.info("No CSV files found in data directory")
        logger.info("Please place CSV files in the 'data/' directory")
        return False
    
    success_count = 0
    total_files = len(csv_files)
    
    for csv_file in csv_files:
        logger.info(f"Processing {csv_file.name}...")
        
        if load_csv_to_products(csv_file):
            success_count += 1
        else:
            logger.error(f"Failed to load {csv_file.name}")
    
    logger.info(f"=== CSV Loading Summary ===")
    logger.info(f"Successfully loaded: {success_count}/{total_files} files")
    
    return success_count == total_files


def create_sample_csv():
    """Create a sample CSV file for testing."""
    
    sample_data = {
        'name': [
            'Laptop Computer',
            'Wireless Mouse',
            'USB Cable',
            'External Hard Drive',
            'Bluetooth Headphones'
        ],
        'description': [
            'High-performance laptop for work and gaming',
            'Ergonomic wireless mouse with precision tracking',
            'High-speed USB 3.0 cable for data transfer',
            '1TB external hard drive for backup storage',
            'Noise-cancelling wireless headphones'
        ],
        'price': [1299.99, 29.99, 12.99, 89.99, 199.99],
        'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
        'stock_quantity': [15, 100, 200, 50, 75]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save sample CSV
    sample_file = data_dir / 'sample_products.csv'
    df.to_csv(sample_file, index=False)
    
    logger.info(f"Created sample CSV file: {sample_file}")
    return sample_file


def main():
    """Main function to load CSV files."""
    
    print("=== CSV Data Loading ===")
    print()
    
    # Check if data directory has CSV files
    csv_files = get_csv_files()
    
    if not csv_files:
        print("No CSV files found in data directory")
        print("Creating sample CSV file for testing...")
        sample_file = create_sample_csv()
        print(f"✓ Created sample file: {sample_file}")
        print()
    
    # Load all CSV files
    if load_all_csv_files():
        print("✓ All CSV files loaded successfully!")
        return True
    else:
        print("✗ Some CSV files failed to load")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 