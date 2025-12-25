#!/bin/bash

# Vercajch Deployment Script
# Usage: ./deploy.sh [command]
# Commands: start, stop, restart, build, logs, status, backup, migrate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="vercajch"
BACKUP_DIR="./backups"

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_msg "Warning: .env file not found. Creating from .env.example..." "$YELLOW"
        if [ -f .env.example ]; then
            cp .env.example .env
            print_msg "Created .env file. Please edit it with your configuration." "$YELLOW"
            exit 1
        else
            print_msg "Error: .env.example not found!" "$RED"
            exit 1
        fi
    fi
}

# Start services
start() {
    print_msg "Starting Vercajch services..." "$BLUE"
    check_env
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    print_msg "Services started successfully!" "$GREEN"
    status
}

# Stop services
stop() {
    print_msg "Stopping Vercajch services..." "$BLUE"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    print_msg "Services stopped." "$GREEN"
}

# Restart services
restart() {
    print_msg "Restarting Vercajch services..." "$BLUE"
    stop
    start
}

# Build images
build() {
    print_msg "Building Vercajch images..." "$BLUE"
    check_env
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --no-cache
    print_msg "Build completed!" "$GREEN"
}

# Build and start
up() {
    print_msg "Building and starting Vercajch..." "$BLUE"
    check_env
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --build
    print_msg "Vercajch is running!" "$GREEN"
    status
}

# Show logs
logs() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    else
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f $SERVICE
    fi
}

# Show status
status() {
    print_msg "\n=== Vercajch Status ===" "$BLUE"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    echo ""
    print_msg "Service URLs:" "$GREEN"
    echo "  - API:     http://localhost:8001"
    echo "  - API Docs: http://localhost:8001/docs"
    echo "  - Web:     http://localhost:3010"
    echo ""
}

# Run database migrations
migrate() {
    print_msg "Running database migrations..." "$BLUE"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec backend alembic upgrade head
    print_msg "Migrations completed!" "$GREEN"
}

# Create database backup
backup() {
    print_msg "Creating database backup..." "$BLUE"
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/vercajch_backup_$TIMESTAMP.sql"

    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T db pg_dump -U vercajch vercajch > $BACKUP_FILE

    if [ -f "$BACKUP_FILE" ]; then
        gzip $BACKUP_FILE
        print_msg "Backup created: ${BACKUP_FILE}.gz" "$GREEN"
    else
        print_msg "Backup failed!" "$RED"
        exit 1
    fi
}

# Restore database from backup
restore() {
    BACKUP_FILE=$1
    if [ -z "$BACKUP_FILE" ]; then
        print_msg "Usage: ./deploy.sh restore <backup_file.sql.gz>" "$RED"
        exit 1
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        print_msg "Backup file not found: $BACKUP_FILE" "$RED"
        exit 1
    fi

    print_msg "Restoring database from $BACKUP_FILE..." "$YELLOW"
    print_msg "Warning: This will overwrite the current database!" "$RED"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gunzip -c $BACKUP_FILE | docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T db psql -U vercajch vercajch
        print_msg "Database restored!" "$GREEN"
    else
        print_msg "Restore cancelled." "$YELLOW"
    fi
}

# Create initial superadmin user
create_admin() {
    print_msg "Creating superadmin user..." "$BLUE"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec backend python -c "
import asyncio
from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import User, Role
from sqlalchemy import select

async def create_admin():
    async with async_session_factory() as session:
        # Get or create superadmin role
        result = await session.execute(select(Role).where(Role.code == 'superadmin'))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(code='superadmin', name='Super Administrator', description='Full system access', is_system_role=True)
            session.add(role)
            await session.commit()
            await session.refresh(role)

        # Check if admin exists
        result = await session.execute(select(User).where(User.email == 'admin@spp-d.sk'))
        if result.scalar_one_or_none():
            print('Admin user already exists!')
            return

        # Create admin user
        admin = User(
            email='admin@spp-d.sk',
            password_hash=get_password_hash('admin123'),
            full_name='System Administrator',
            role_id=role.id,
            is_active=True,
            can_access_web=True,
            can_access_mobile=True
        )
        session.add(admin)
        await session.commit()
        print('Admin user created!')
        print('Email: admin@spp-d.sk')
        print('Password: admin123')
        print('Please change the password after first login!')

asyncio.run(create_admin())
"
    print_msg "Done!" "$GREEN"
}

# Development mode
dev() {
    print_msg "Starting in development mode..." "$BLUE"
    check_env
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p $PROJECT_NAME up -d
    print_msg "Development environment started!" "$GREEN"
    echo ""
    echo "Services:"
    echo "  - API:     http://localhost:8000"
    echo "  - Web Dev: http://localhost:5173"
    echo ""
}

# Clean up everything
clean() {
    print_msg "Cleaning up Vercajch..." "$YELLOW"
    print_msg "Warning: This will remove all containers, volumes, and images!" "$RED"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v --rmi all
        print_msg "Cleanup completed!" "$GREEN"
    else
        print_msg "Cleanup cancelled." "$YELLOW"
    fi
}

# Show help
help() {
    echo ""
    print_msg "Vercajch Deployment Script" "$BLUE"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start        Start all services"
    echo "  stop         Stop all services"
    echo "  restart      Restart all services"
    echo "  build        Build Docker images"
    echo "  up           Build and start services"
    echo "  logs [svc]   Show logs (optionally for specific service)"
    echo "  status       Show service status"
    echo "  migrate      Run database migrations"
    echo "  backup       Create database backup"
    echo "  restore      Restore database from backup"
    echo "  create-admin Create initial admin user"
    echo "  dev          Start in development mode"
    echo "  clean        Remove all containers, volumes, and images"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh up           # Build and start everything"
    echo "  ./deploy.sh logs backend # Show backend logs"
    echo "  ./deploy.sh backup       # Create database backup"
    echo ""
}

# Main
case "${1}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    build)
        build
        ;;
    up)
        up
        ;;
    logs)
        logs $2
        ;;
    status)
        status
        ;;
    migrate)
        migrate
        ;;
    backup)
        backup
        ;;
    restore)
        restore $2
        ;;
    create-admin)
        create_admin
        ;;
    dev)
        dev
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        help
        ;;
esac
