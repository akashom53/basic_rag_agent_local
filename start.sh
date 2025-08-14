#!/bin/bash

echo "🚀 Starting AI Support Bot..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Enable Docker BuildKit and Bake for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export COMPOSE_BAKE=true

# Check if NVIDIA Docker runtime is available (for GPU support)
if docker info | grep -q "nvidia"; then
    echo "✅ NVIDIA Docker runtime detected - GPU support enabled"
else
    echo "⚠️  NVIDIA Docker runtime not detected - running in CPU mode"
fi

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Start services
echo "🔧 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Service status:"
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "🎉 AI Support Bot is starting up!"
echo "📱 API will be available at: http://localhost:8000"
echo "🔍 Health check: http://localhost:8000/health"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
