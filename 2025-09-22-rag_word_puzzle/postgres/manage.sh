#!/bin/bash

# PostgreSQL RAG Database Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Default values
POSTGRES_DB=${POSTGRES_DB:-rag_database}
POSTGRES_USER=${POSTGRES_USER:-rag_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-rag_password}

function print_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|shell|backup|restore|reset}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the PostgreSQL container"
    echo "  stop     - Stop the PostgreSQL container"
    echo "  restart  - Restart the PostgreSQL container"
    echo "  status   - Show container status"
    echo "  logs     - Show container logs"
    echo "  shell    - Open psql shell to database"
    echo "  backup   - Create database backup"
    echo "  restore  - Restore database from backup"
    echo "  reset    - Reset database (WARNING: destroys all data)"
}

function start_db() {
    echo -e "${GREEN}Starting PostgreSQL database...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Waiting for database to be ready...${NC}"
    sleep 5
    docker-compose exec postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
    echo -e "${GREEN}Database is ready!${NC}"
}

function stop_db() {
    echo -e "${YELLOW}Stopping PostgreSQL database...${NC}"
    docker-compose down
    echo -e "${GREEN}Database stopped.${NC}"
}

function restart_db() {
    stop_db
    start_db
}

function show_status() {
    echo -e "${GREEN}Container status:${NC}"
    docker-compose ps
}

function show_logs() {
    echo -e "${GREEN}Database logs:${NC}"
    docker-compose logs postgres
}

function open_shell() {
    echo -e "${GREEN}Opening database shell...${NC}"
    docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
}

function backup_db() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${timestamp}.sql"
    echo -e "${GREEN}Creating backup: ${backup_file}${NC}"
    docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $backup_file
    echo -e "${GREEN}Backup created: ${backup_file}${NC}"
}

function restore_db() {
    if [ -z "$2" ]; then
        echo -e "${RED}Error: Please specify backup file${NC}"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    backup_file="$2"
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}Error: Backup file '$backup_file' not found${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Restoring database from: ${backup_file}${NC}"
    docker-compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < $backup_file
    echo -e "${GREEN}Database restored from: ${backup_file}${NC}"
}

function reset_db() {
    echo -e "${RED}WARNING: This will destroy all data!${NC}"
    read -p "Are you sure you want to reset the database? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo -e "${YELLOW}Resetting database...${NC}"
        docker-compose down -v
        docker-compose up -d
        echo -e "${GREEN}Database reset complete.${NC}"
    else
        echo -e "${GREEN}Reset cancelled.${NC}"
    fi
}

# Main script logic
case "$1" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db "$@"
        ;;
    reset)
        reset_db
        ;;
    *)
        print_usage
        exit 1
        ;;
esac