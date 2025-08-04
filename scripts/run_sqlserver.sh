#!/bin/bash

# SQL Server Docker Container Management Script
# This script helps manage the SQL Server container for local development

set -e

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
    export SQL_USER=sa
    export SQL_PASSWORD=YourStrong@Passw0rd
    export SQL_SERVER=localhost
    export SQL_PORT=1433
    export SQL_DB=master
    export DOCKER_IMAGE=mcr.microsoft.com/mssql/server:2022-latest
    export CONTAINER_NAME=sqlserver-demo
fi

# Default values if not set in .env
export SQL_USER=${SQL_USER:-sa}
export SQL_PASSWORD=${SQL_PASSWORD:-YourStrong@Passw0rd}
export SQL_SERVER=${SQL_SERVER:-localhost}
export SQL_PORT=${SQL_PORT:-1433}
export SQL_DB=${SQL_DB:-master}
export DOCKER_IMAGE=${DOCKER_IMAGE:-mcr.microsoft.com/mssql/server:2022-latest}
export CONTAINER_NAME=${CONTAINER_NAME:-sqlserver-demo}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if container exists
container_exists() {
    docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if container is running
container_running() {
    docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to start the SQL Server container
start_container() {
    print_status "Starting SQL Server container..."
    
    # Check if container already exists
    if container_exists; then
        if container_running; then
            print_warning "Container ${CONTAINER_NAME} is already running."
            return 0
        else
            print_status "Starting existing container ${CONTAINER_NAME}..."
            docker start ${CONTAINER_NAME}
        fi
    else
        print_status "Creating and starting new SQL Server container..."
        
        # Pull the image if it doesn't exist
        if ! docker images | grep -q "$(echo $DOCKER_IMAGE | cut -d':' -f1)"; then
            print_status "Pulling SQL Server image..."
            docker pull $DOCKER_IMAGE
        fi
        
        # Create and start the container
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${SQL_PORT}:1433 \
            -e "ACCEPT_EULA=Y" \
            -e "MSSQL_SA_PASSWORD=${SQL_PASSWORD}" \
            -e "MSSQL_PID=Developer" \
            --platform linux/amd64 \
            $DOCKER_IMAGE
    fi
    
    # Wait for SQL Server to be ready
    print_status "Waiting for SQL Server to be ready..."
    sleep 10
    
    # Check if container is running
    if container_running; then
        print_success "SQL Server container is running!"
        print_status "Connection details:"
        print_status "  Server: ${SQL_SERVER}:${SQL_PORT}"
        print_status "  Database: ${SQL_DB}"
        print_status "  Username: ${SQL_USER}"
        print_status "  Password: ${SQL_PASSWORD}"
        print_status ""
        print_status "You can now run your Python scripts to connect to the database."
    else
        print_error "Failed to start SQL Server container."
        exit 1
    fi
}

# Function to stop the SQL Server container
stop_container() {
    print_status "Stopping SQL Server container..."
    
    if container_exists; then
        if container_running; then
            docker stop ${CONTAINER_NAME}
            print_success "SQL Server container stopped."
        else
            print_warning "Container ${CONTAINER_NAME} is not running."
        fi
    else
        print_warning "Container ${CONTAINER_NAME} does not exist."
    fi
}

# Function to remove the SQL Server container
remove_container() {
    print_status "Removing SQL Server container..."
    
    if container_exists; then
        if container_running; then
            docker stop ${CONTAINER_NAME}
        fi
        docker rm ${CONTAINER_NAME}
        print_success "SQL Server container removed."
    else
        print_warning "Container ${CONTAINER_NAME} does not exist."
    fi
}

# Function to show container status
show_status() {
    print_status "SQL Server Container Status:"
    echo ""
    
    if container_exists; then
        if container_running; then
            print_success "Container ${CONTAINER_NAME} is running"
            echo ""
            docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            print_warning "Container ${CONTAINER_NAME} exists but is not running"
            echo ""
            docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        fi
    else
        print_warning "Container ${CONTAINER_NAME} does not exist"
    fi
    
    echo ""
    print_status "Connection Configuration:"
    print_status "  Server: ${SQL_SERVER}:${SQL_PORT}"
    print_status "  Database: ${SQL_DB}"
    print_status "  Username: ${SQL_USER}"
    print_status "  Password: ${SQL_PASSWORD}"
}

# Function to show logs
show_logs() {
    if container_exists; then
        print_status "Showing logs for container ${CONTAINER_NAME}..."
        docker logs ${CONTAINER_NAME}
    else
        print_error "Container ${CONTAINER_NAME} does not exist."
    fi
}

# Function to show help
show_help() {
    echo "SQL Server Docker Container Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the SQL Server container"
    echo "  stop      Stop the SQL Server container"
    echo "  restart   Restart the SQL Server container"
    echo "  remove    Remove the SQL Server container"
    echo "  status    Show container status and configuration"
    echo "  logs      Show container logs"
    echo "  help      Show this help message"
    echo ""
    echo "Environment variables (from .env file):"
    echo "  SQL_USER         SQL Server username (default: sa)"
    echo "  SQL_PASSWORD     SQL Server password"
    echo "  SQL_SERVER       SQL Server host (default: localhost)"
    echo "  SQL_PORT         SQL Server port (default: 1433)"
    echo "  SQL_DB           SQL Server database (default: master)"
    echo "  DOCKER_IMAGE     Docker image (default: mcr.microsoft.com/mssql/server:2022-latest)"
    echo "  CONTAINER_NAME   Container name (default: sqlserver-demo)"
    echo ""
    echo "Examples:"
    echo "  $0 start         # Start the container"
    echo "  $0 status        # Check container status"
    echo "  $0 stop          # Stop the container"
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            stop_container
            start_container
            ;;
        remove)
            remove_container
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 