#!/bin/bash

# Docker setup validation script

echo "🔍 Validating Docker setup for Agent Task Assignment System..."
echo ""

# Check if Docker files exist
echo "📁 Checking Docker files..."
files=(
    "Dockerfile"
    "Dockerfile.prod"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    ".dockerignore"
    "nginx.conf"
    "docker-run.sh"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""

# Check if .env.example exists
if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"
else
    echo "❌ .env.example missing"
fi

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env exists"
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "✅ OPENAI_API_KEY configured"
    else
        echo "⚠️  OPENAI_API_KEY not configured (OpenAI features will be disabled)"
    fi
else
    echo "⚠️  .env not found - will be created from .env.example"
fi

echo ""

# Check script permissions
if [ -x "docker-run.sh" ]; then
    echo "✅ docker-run.sh is executable"
else
    echo "⚠️  docker-run.sh needs execute permission: chmod +x docker-run.sh"
fi

echo ""

# Validate Docker Compose syntax
echo "🔧 Validating Docker Compose files..."
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo "✅ docker-compose.yml syntax is valid"
    else
        echo "❌ docker-compose.yml has syntax errors"
    fi
    
    if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
        echo "✅ docker-compose.prod.yml syntax is valid"
    else
        echo "❌ docker-compose.prod.yml has syntax errors"
    fi
else
    echo "⚠️  docker-compose not found - install Docker Compose to validate"
fi

echo ""
echo "📋 Next steps:"
echo "1. Ensure Docker and Docker Compose are installed"
echo "2. Copy .env.example to .env and add your OPENAI_API_KEY"
echo "3. Run: ./docker-run.sh"
echo "4. Access API at: http://localhost:8001"
echo ""
echo "📚 For detailed instructions, see DOCKER.md"
