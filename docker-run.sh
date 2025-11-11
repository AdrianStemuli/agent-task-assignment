#!/bin/bash

# Docker run script for Agent Task Assignment System

echo "🐳 Starting Agent Task Assignment System with Docker..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    echo ""
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OPENAI_API_KEY not configured in .env"
    echo "   The API will start but OpenAI features will be disabled."
    echo ""
fi

# Build and run with docker-compose
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting container..."
docker-compose up -d

echo ""
echo "✅ Container started successfully!"
echo ""
echo "🌐 API is available at: http://localhost:8001"
echo "📚 API Documentation: http://localhost:8001/docs"
echo "🔍 Health Check: http://localhost:8001/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop service:  docker-compose down"
echo "   Restart:       docker-compose restart"
echo "   Shell access:  docker-compose exec agent-task-assignment bash"
echo ""

# Show container status
echo "📊 Container Status:"
docker-compose ps
