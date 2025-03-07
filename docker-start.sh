#!/bin/bash

# Script to start Docker services for Quiz App

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}   Quiz App Docker Environment Manager   ${NC}"
echo -e "${BLUE}==============================================${NC}"

# Function to start development environment
start_dev() {
    echo -e "${GREEN}Starting development environment...${NC}"
    sudo docker-compose up -d
    
    echo -e "${GREEN}Services started:${NC}"
    echo -e "  - Frontend: http://localhost:3001"
    echo -e "  - Backend API: http://localhost:9999"
    echo -e "  - PgAdmin: http://localhost:5051"
    echo -e "    (email: admin@example.com, password: admin)"
}

# Function to start production environment
start_prod() {
    echo -e "${GREEN}Starting production environment...${NC}"
    sudo docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}Services started:${NC}"
    echo -e "  - Frontend: http://localhost"
    echo -e "  - Backend API: http://localhost:9999"
    echo -e "  - PgAdmin: http://localhost:5051"
    echo -e "    (email: admin@example.com, password: admin)"
}

# Function to stop environment
stop_env() {
    if [ "$1" == "prod" ]; then
        echo -e "${GREEN}Stopping production environment...${NC}"
        sudo docker-compose -f docker-compose.prod.yml down
    else
        echo -e "${GREEN}Stopping development environment...${NC}"
        sudo docker-compose down
    fi
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Usage:${NC}"
    echo -e "  ./docker-start.sh dev     - Start development environment"
    echo -e "  ./docker-start.sh prod    - Start production environment"
    echo -e "  ./docker-start.sh stop    - Stop development environment"
    echo -e "  ./docker-start.sh stop-prod - Stop production environment"
    exit 1
fi

# Process arguments
case "$1" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    stop)
        stop_env "dev"
        ;;
    stop-prod)
        stop_env "prod"
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo -e "${RED}Usage:${NC}"
        echo -e "  ./docker-start.sh dev     - Start development environment"
        echo -e "  ./docker-start.sh prod    - Start production environment"
        echo -e "  ./docker-start.sh stop    - Stop development environment"
        echo -e "  ./docker-start.sh stop-prod - Stop production environment"
        exit 1
        ;;
esac

exit 0
