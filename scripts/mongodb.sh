#!/bin/bash

# MongoDB management script for Memori SDK

set -e

case "${1:-help}" in
    start)
        echo "Starting MongoDB with Docker Compose..."
        docker-compose up -d mongodb
        echo "MongoDB started successfully!"
        echo "Connection string: mongodb://memori:memori@localhost:27017/memori"
        ;;
    stop)
        echo "Stopping MongoDB..."
        docker-compose down
        echo "MongoDB stopped successfully!"
        ;;
    restart)
        echo "Restarting MongoDB..."
        docker-compose restart mongodb
        echo "MongoDB restarted successfully!"
        ;;
    logs)
        echo "Showing MongoDB logs..."
        docker-compose logs -f mongodb
        ;;
    status)
        echo "MongoDB status:"
        docker-compose ps mongodb
        ;;
    test)
        echo "Running MongoDB migration tests..."
        uv run tests/build/mongodb.py
        ;;
    reset)
        echo "Resetting MongoDB data..."
        docker-compose down -v
        docker-compose up -d mongodb
        echo "MongoDB reset successfully!"
        ;;
    shell)
        echo "Connecting to MongoDB shell..."
        docker-compose exec mongodb mongosh mongodb://memori:memori@localhost:27017/memori
        ;;
    ui)
        echo "Starting MongoDB Express UI..."
        docker-compose up -d mongo-express
        echo "MongoDB Express available at: http://localhost:8081"
        ;;
    help|*)
        echo "MongoDB Management Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  start     Start MongoDB container"
        echo "  stop      Stop MongoDB container"
        echo "  restart   Restart MongoDB container"
        echo "  logs      Show MongoDB logs"
        echo "  status    Show MongoDB container status"
        echo "  test      Run MongoDB migration tests"
        echo "  reset     Reset MongoDB data (removes all data)"
        echo "  shell     Connect to MongoDB shell"
        echo "  ui        Start MongoDB Express web UI"
        echo "  help      Show this help message"
        ;;
esac
