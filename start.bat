@echo off
echo 🚀 Starting AI Support Bot...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Enable Docker BuildKit and Bake for faster builds
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1
set COMPOSE_BAKE=true

REM Check if NVIDIA Docker runtime is available
docker info | findstr "nvidia" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  NVIDIA Docker runtime not detected - running in CPU mode
) else (
    echo ✅ NVIDIA Docker runtime detected - GPU support enabled
)

REM Pull latest images
echo 📥 Pulling latest Docker images...
docker-compose pull

REM Start services
echo 🔧 Starting services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service status
echo 📊 Service status:
docker-compose ps

REM Show logs
echo 📋 Recent logs:
docker-compose logs --tail=20

echo.
echo 🎉 AI Support Bot is starting up!
echo 📱 API will be available at: http://localhost:8000
echo 🔍 Health check: http://localhost:8000/health
echo 📚 API docs: http://localhost:8000/docs
echo.
echo 📝 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
pause
