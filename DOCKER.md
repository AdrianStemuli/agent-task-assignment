# Docker Deployment Guide

This guide covers how to deploy the Agent Task Assignment System using Docker.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with your OpenAI API key

### Development Deployment

1. **Clone and setup environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your OPENAI_API_KEY
   nano .env
   ```

2. **Run with Docker Compose:**
   ```bash
   # Quick start script
   ./docker-run.sh
   
   # Or manually:
   docker-compose up -d
   ```

3. **Access the API:**
   - API: http://localhost:8001
   - Documentation: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

### Production Deployment

For production environments with nginx reverse proxy:

```bash
# Build and run production setup
docker-compose -f docker-compose.prod.yml up -d

# Access via nginx (port 80)
curl http://localhost/health
```

## Docker Files Overview

### Core Files
- `Dockerfile` - Development container
- `Dockerfile.prod` - Production container with multi-stage build
- `docker-compose.yml` - Development orchestration
- `docker-compose.prod.yml` - Production orchestration with nginx
- `.dockerignore` - Files to exclude from build context

### Configuration Files
- `nginx.conf` - Nginx reverse proxy configuration
- `docker-run.sh` - Quick start script

## Environment Variables

Set these in your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
DEBUG=false
```

## Docker Commands

### Basic Operations
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

### Development Commands
```bash
# Shell access
docker-compose exec agent-task-assignment bash

# View container status
docker-compose ps

# Remove everything (including volumes)
docker-compose down -v --remove-orphans
```

### Production Commands
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale agent-task-assignment=3

# Update production
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Container Architecture

### Development Container
- **Base Image:** `python:3.9-slim`
- **Port:** 8001
- **User:** appuser (non-root)
- **Health Check:** HTTP GET /health
- **Restart Policy:** unless-stopped

### Production Container
- **Multi-stage build** for smaller image size
- **Multiple workers** via uvicorn
- **Resource limits** (512MB memory)
- **Nginx reverse proxy** with rate limiting
- **Security headers** and CORS configuration

## Networking

### Development
- **Network:** `agent-network` (bridge)
- **Exposed Ports:** 8001

### Production
- **Network:** `agent-network` (bridge)
- **Exposed Ports:** 80 (nginx), 443 (HTTPS)
- **Internal:** 8001 (app container)

## Security Features

### Container Security
- Non-root user execution
- Minimal base image (slim)
- Security headers via nginx
- Resource limits

### Network Security
- Rate limiting (10 req/s with burst)
- CORS configuration
- Optional HTTPS/SSL support

## Monitoring & Health Checks

### Health Checks
- **Endpoint:** `/health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds
- **Retries:** 3

### Logging
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Service-specific logs
docker-compose logs agent-task-assignment
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill existing process
   lsof -ti:8001 | xargs kill -9
   ```

2. **Permission denied:**
   ```bash
   # Fix script permissions
   chmod +x docker-run.sh
   ```

3. **OpenAI API not working:**
   - Check `.env` file has correct API key
   - Verify API key format: `sk-...`

4. **Container won't start:**
   ```bash
   # Check logs
   docker-compose logs agent-task-assignment
   
   # Rebuild image
   docker-compose build --no-cache
   ```

### Debug Mode
```bash
# Run with debug output
DEBUG=true docker-compose up

# Interactive shell
docker-compose run --rm agent-task-assignment bash
```

## Performance Tuning

### Production Optimizations
- **Workers:** 4 uvicorn workers (adjust based on CPU cores)
- **Memory:** 512MB limit (adjust based on usage)
- **Rate Limiting:** 10 req/s (adjust based on needs)

### Scaling
```bash
# Horizontal scaling
docker-compose -f docker-compose.prod.yml up -d --scale agent-task-assignment=3

# Load balancer will distribute requests across instances
```

## Backup & Persistence

Currently, the application is stateless. All data is ephemeral.

For persistent storage, add volumes:
```yaml
volumes:
  - ./data:/app/data
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.prod.yml up -d
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify health: `curl http://localhost:8001/health`
3. Review this documentation
4. Check the main README.md for API usage
