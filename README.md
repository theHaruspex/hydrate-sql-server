# SQL Server Python Project

A Python 3.11 project that connects to a local SQL Server instance running in Docker. This project provides a complete setup for working with SQL Server using both `pyodbc` and `SQLAlchemy`, with support for bulk data loading from CSV files.

## Features

- **Docker-based SQL Server**: Easy setup with Microsoft SQL Server 2022 running in Docker
- **Dual Connection Support**: Both `pyodbc` and `SQLAlchemy` connection methods
- **CSV Data Loading**: Bulk insert functionality for loading CSV files into SQL Server
- **M3 Mac Support**: Optimized for ARM64 architecture with proper platform handling
- **Environment Configuration**: Secure configuration management with `.env` files
- **Helper Scripts**: Bash scripts for easy container management

## Prerequisites

- Python 3.13+ (tested with Python 3.13.5)
- Docker Desktop
- Microsoft ODBC Driver 18 for SQL Server (for macOS)

### Installing ODBC Driver on macOS

```bash
# Using Homebrew
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18 mssql-tools18

# Or download directly from Microsoft
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hydrate-sql-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and customize it:

```bash
cp env.example .env
```

Edit `.env` with your preferred settings:

```env
# SQL Server Configuration
SQL_USER=sa
SQL_PASSWORD=YourStrong@Passw0rd
SQL_SERVER=localhost
SQL_PORT=1433
SQL_DB=master

# Docker Configuration
DOCKER_IMAGE=mcr.microsoft.com/mssql/server:2022-latest
CONTAINER_NAME=sqlserver-demo
```

**⚠️ Security Note**: The default password is for demo purposes only. Change it for production use.

### 3. Start SQL Server Container

Using the helper script:

```bash
# Start the container
./scripts/run_sqlserver.sh start

# Check status
./scripts/run_sqlserver.sh status

# View logs
./scripts/run_sqlserver.sh logs
```

Or using Docker Compose:

```bash
cd Docker
docker-compose up -d
```

### 4. Test Database Connection

```bash
# Test both connection methods
python src/database.py
```

This will:
- List available ODBC drivers
- Test `pyodbc` connection
- Test `SQLAlchemy` connection
- Display server version information

### 5. Initialize Database Schema

```bash
# Create products table and sample data
python db/init_schema.py
```

### 6. Load CSV Data

Place your CSV files in the `data/` directory, then:

```bash
# Load all CSV files in the data directory
python db/load_csv.py
```

The script will automatically create a sample CSV if none exists.

## Project Structure

```
hydrate-sql-server/
├── src/                    # Python source code
│   ├── __init__.py
│   └── database.py        # Database connection utilities
├── db/                    # Database scripts
│   ├── __init__.py
│   ├── init_schema.py     # Schema initialization
│   └── load_csv.py        # CSV data loading
├── data/                  # CSV files for data loading
│   └── .gitkeep
├── scripts/               # Helper shell scripts
│   └── run_sqlserver.sh  # SQL Server container management
├── Docker/                # Docker configuration
│   └── docker-compose.yml # Local development orchestration
├── requirements.txt       # Python dependencies
├── env.example           # Environment configuration template
└── README.md            # This file
```

## Usage Examples

### Basic Connection Test

```python
from src.database import SQLServerConnection

# Create connection manager
conn_manager = SQLServerConnection()

# Test connections
conn_manager.test_pyodbc_connection()
conn_manager.test_sqlalchemy_connection()

# List available drivers
drivers = conn_manager.get_odbc_drivers()
print(f"Available drivers: {drivers}")
```

### Query Execution with pyodbc

```python
from src.database import SQLServerConnection

conn_manager = SQLServerConnection()

# Execute a SELECT query
result = conn_manager.execute_query_pyodbc("SELECT * FROM products")
print(result)

# Execute an INSERT query
conn_manager.execute_query_pyodbc(
    "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
    ("New Product", 29.99, "Electronics")
)
```

### Query Execution with SQLAlchemy

```python
from src.database import SQLServerConnection

conn_manager = SQLServerConnection()

# Execute a SELECT query
result = conn_manager.execute_query_sqlalchemy("SELECT * FROM products")
print(result)

# Execute an INSERT query
conn_manager.execute_query_sqlalchemy(
    "INSERT INTO products (name, price, category) VALUES (:name, :price, :category)",
    {"name": "New Product", "price": 29.99, "category": "Electronics"}
)
```

### Bulk Data Loading

```python
import pandas as pd
from src.database import SQLServerConnection

# Load CSV data
df = pd.read_csv('data/products.csv')

# Get SQLAlchemy engine
conn_manager = SQLServerConnection()
engine = conn_manager.get_sqlalchemy_engine()

# Bulk insert
df.to_sql('products', engine, if_exists='append', index=False)
```

## Container Management

The `scripts/run_sqlserver.sh` script provides easy container management:

```bash
# Start container
./scripts/run_sqlserver.sh start

# Stop container
./scripts/run_sqlserver.sh stop

# Restart container
./scripts/run_sqlserver.sh restart

# Remove container
./scripts/run_sqlserver.sh remove

# Check status
./scripts/run_sqlserver.sh status

# View logs
./scripts/run_sqlserver.sh logs

# Show help
./scripts/run_sqlserver.sh help
```

## Docker Compose

For more complex setups, use Docker Compose:

```bash
cd Docker
docker-compose up -d    # Start services
docker-compose down     # Stop services
docker-compose logs     # View logs
```

## Troubleshooting

### Connection Issues

1. **No ODBC Drivers Found**:
   ```bash
   # Install Microsoft ODBC Driver 18
   brew install msodbcsql18
   ```

2. **Container Won't Start**:
   ```bash
   # Check Docker is running
   docker info
   
   # Check container logs
   ./scripts/run_sqlserver.sh logs
   ```

3. **Port Already in Use**:
   ```bash
   # Check what's using port 1433
   lsof -i :1433
   
   # Change port in .env file
   SQL_PORT=1434
   ```

4. **SQLAlchemy Timeout Issues**:
   - The project uses pyodbc for reliable connections
   - SQLAlchemy may timeout on initial connection (known issue)
   - All functionality works with pyodbc connection method

### M3 Mac Specific Issues

The project is configured to handle ARM64 architecture:

- Uses `--platform linux/amd64` for SQL Server container
- ODBC driver compatibility is handled automatically
- Architecture mismatch warnings are safely ignored
- **Tested and working on M3 Mac with Python 3.13.5**

### Performance Tips

1. **Bulk Inserts**: Use the CSV loading script for large datasets
2. **Connection Pooling**: SQLAlchemy handles connection pooling automatically
3. **Indexes**: The schema includes indexes for better query performance

## Development

### Adding New Tables

1. Create a new script in `db/` directory
2. Use the `SQLServerConnection` class for database operations
3. Follow the pattern in `init_schema.py`

### Extending Data Loading

1. Modify `load_csv.py` to support new table schemas
2. Add column mapping for different CSV formats
3. Implement data validation and cleaning

### Environment Variables

All configuration is managed through environment variables:

- `SQL_USER`: Database username (default: sa)
- `SQL_PASSWORD`: Database password
- `SQL_SERVER`: Server hostname (default: localhost)
- `SQL_PORT`: Server port (default: 1433)
- `SQL_DB`: Database name (default: master)
- `DOCKER_IMAGE`: SQL Server Docker image
- `CONTAINER_NAME`: Docker container name

## Security Considerations

1. **Change Default Password**: Always change the default password in production
2. **Environment Files**: Never commit `.env` files to version control
3. **Network Security**: Use VPN or firewall rules in production
4. **Data Encryption**: Enable SSL/TLS for production deployments

## Future Enhancements

This project is designed to expand into a data ingestion pipeline:

- **Scheduled Jobs**: Add cron-like scheduling for data loading
- **Data Validation**: Implement schema validation and data quality checks
- **Monitoring**: Add metrics and alerting for database operations
- **API Layer**: Create REST API for data access
- **Multi-Database Support**: Extend to support other database systems

## Testing Status

✅ **Fully Tested and Working:**
- Python 3.13.5 on M3 Mac
- SQL Server 2022 Docker container
- pyodbc connections (primary method)
- CSV data loading with bulk insert
- Container management scripts
- Schema initialization and data verification

⚠️ **Known Issues:**
- SQLAlchemy connections may timeout (pyodbc works perfectly)
- pandas deprecation warning about pyarrow (doesn't affect functionality)

## License

This project is for educational and development purposes. Please ensure compliance with Microsoft SQL Server licensing for production use. 