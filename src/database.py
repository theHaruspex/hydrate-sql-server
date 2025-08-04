import os
import logging
import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SQLServerConnection:
    """SQL Server connection manager with both pyodbc and SQLAlchemy support."""
    
    def __init__(self):
        self.sql_user = os.getenv('SQL_USER', 'sa')
        self.sql_password = os.getenv('SQL_PASSWORD', 'YourStrong@Passw0rd')
        self.sql_server = os.getenv('SQL_SERVER', 'localhost')
        self.sql_port = os.getenv('SQL_PORT', '1433')
        self.sql_db = os.getenv('SQL_DB', 'master')
        
        # Build connection strings
        self.odbc_connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.sql_server},{self.sql_port};"
            f"DATABASE={self.sql_db};"
            f"UID={self.sql_user};"
            f"PWD={self.sql_password};"
            f"TrustServerCertificate=yes;"
        )
        
        self.sqlalchemy_url = (
            f"mssql+pyodbc://{self.sql_user}:{self.sql_password}@"
            f"{self.sql_server}:{self.sql_port}/{self.sql_db}?"
            f"driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
            f"&timeout=30&connection_timeout=30"
        )
    
    def get_odbc_drivers(self):
        """List available ODBC drivers for SQL Server."""
        drivers = pyodbc.drivers()
        sql_server_drivers = [driver for driver in drivers if 'SQL Server' in driver]
        logger.info(f"Available SQL Server ODBC drivers: {sql_server_drivers}")
        return sql_server_drivers
    
    def test_pyodbc_connection(self):
        """Test connection using pyodbc."""
        try:
            # Check available drivers
            drivers = self.get_odbc_drivers()
            if not drivers:
                logger.error("No SQL Server ODBC drivers found!")
                return False
            
            # Try to connect
            conn = pyodbc.connect(self.odbc_connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            logger.info(f"Successfully connected to SQL Server using pyodbc")
            logger.info(f"Server version: {version}")
            conn.close()
            return True
            
        except pyodbc.Error as e:
            logger.error(f"pyodbc connection failed: {e}")
            return False
    
    def test_sqlalchemy_connection(self):
        """Test connection using SQLAlchemy."""
        try:
            engine = create_engine(self.sqlalchemy_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION"))
                version = result.fetchone()[0]
                logger.info(f"Successfully connected to SQL Server using SQLAlchemy")
                logger.info(f"Server version: {version}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy connection failed: {e}")
            return False
    
    def get_pyodbc_connection(self):
        """Get a pyodbc connection."""
        try:
            return pyodbc.connect(self.odbc_connection_string)
        except pyodbc.Error as e:
            logger.error(f"Failed to create pyodbc connection: {e}")
            raise
    
    def get_sqlalchemy_engine(self):
        """Get a SQLAlchemy engine."""
        try:
            return create_engine(self.sqlalchemy_url)
        except SQLAlchemyError as e:
            logger.error(f"Failed to create SQLAlchemy engine: {e}")
            raise
    
    def execute_query_pyodbc(self, query, params=None):
        """Execute a query using pyodbc."""
        try:
            conn = self.get_pyodbc_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(results, columns=columns)
                conn.close()
                return df
            else:
                conn.commit()
                conn.close()
                logger.info(f"Query executed successfully: {query[:50]}...")
                return True
                
        except pyodbc.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_sqlalchemy(self, query, params=None):
        """Execute a query using SQLAlchemy."""
        try:
            engine = self.get_sqlalchemy_engine()
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                if query.strip().upper().startswith('SELECT'):
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    return df
                else:
                    conn.commit()
                    logger.info(f"Query executed successfully: {query[:50]}...")
                    return True
                    
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            raise


def test_connections():
    """Test both connection methods and list available drivers."""
    conn_manager = SQLServerConnection()
    
    print("=== SQL Server Connection Test ===")
    print(f"Server: {conn_manager.sql_server}:{conn_manager.sql_port}")
    print(f"Database: {conn_manager.sql_db}")
    print(f"User: {conn_manager.sql_user}")
    print()
    
    # List available drivers
    print("=== Available ODBC Drivers ===")
    drivers = conn_manager.get_odbc_drivers()
    if drivers:
        for driver in drivers:
            print(f"✓ {driver}")
    else:
        print("✗ No SQL Server ODBC drivers found!")
        print("Please install the Microsoft ODBC Driver for SQL Server")
    print()
    
    # Test pyodbc connection
    print("=== Testing pyodbc Connection ===")
    if conn_manager.test_pyodbc_connection():
        print("✓ pyodbc connection successful")
    else:
        print("✗ pyodbc connection failed")
    print()
    
    # Test SQLAlchemy connection
    print("=== Testing SQLAlchemy Connection ===")
    if conn_manager.test_sqlalchemy_connection():
        print("✓ SQLAlchemy connection successful")
    else:
        print("✗ SQLAlchemy connection failed")
    print()


if __name__ == "__main__":
    test_connections() 