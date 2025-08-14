# Setup Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **Docker**: Version 20.10+ with Docker Compose
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: At least 10GB free space
- **GPU** (Optional): NVIDIA GPU with CUDA support for accelerated inference

### Software Dependencies

- **Docker Desktop**: For containerized deployment
- **NVIDIA Docker Runtime**: For GPU acceleration (optional)
- **Git**: For version control
- **Python 3.8+**: For local development (optional)

## Quick Start (Docker)

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd tantorinc
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit configuration (optional)
nano .env
```

**Default Configuration:**
```bash
# Database
DATABASE_USER=trantor
DATABASE_PASSWORD=trantor_pass
DATABASE_NAME=trantor_db

# Embedding Model
EMBED_MODEL=BAAI/bge-small-en-v1.5

# LLM Configuration
LLM_MODEL=ollama:qwen2.5:7b-instruct
GPU_LAYERS=20

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Start Services

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Manual Start:**
```bash
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## Local Development Setup

### 1. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

**Option A: Docker PostgreSQL**
```bash
# Start only the database
docker run -d \
  --name pgvector \
  -e POSTGRES_USER=trantor \
  -e POSTGRES_PASSWORD=trantor_pass \
  -e POSTGRES_DB=trantor_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Wait for startup
sleep 10

# Initialize schema
docker exec -i pgvector psql -U trantor -d trantor_db < schema/DB_SCHEMA_pgvector.sql
```

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL + pgvector
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-16-pgvector

# macOS:
brew install postgresql
brew install pgvector

# Windows: Download from postgresql.org
```

### 3. Environment Variables

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://trantor:trantor_pass@localhost:5432/trantor_db
EMBED_MODEL=BAAI/bge-small-en-v1.5
LLM_MODEL=ollama:qwen2.5:7b-instruct
GPU_LAYERS=0
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### 4. Run Application

```bash
# Start the FastAPI application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## GPU Instance Deployment

### Google Colab

**1. Upload Code**
```python
# Upload your project files
from google.colab import files
uploaded = files.upload()

# Extract if needed
!unzip tantorinc.zip
%cd tantorinc
```

**2. Install Dependencies**
```bash
# Install Docker
!curl -fsSL https://get.docker.com -o get-docker.sh
!sh get-docker.sh

# Install NVIDIA Docker runtime
!distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
!curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
!curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

!sudo apt-get update
!sudo apt-get install -y nvidia-docker2
!sudo systemctl restart docker
```

**3. Configure Environment**
```bash
# Set environment variables
import os
os.environ['DATABASE_USER'] = 'trantor'
os.environ['DATABASE_PASSWORD'] = 'trantor_pass'
os.environ['DATABASE_NAME'] = 'trantor_db'
os.environ['LLM_MODEL'] = 'ollama:qwen2.5:7b-instruct'
os.environ['GPU_LAYERS'] = '20'
```

**4. Start Services**
```bash
# Start with GPU support
!docker-compose up -d

# Check status
!docker-compose ps
```

### Google Cloud Platform (GCP)

**1. Create VM Instance**
```bash
# Create GPU-enabled instance
gcloud compute instances create ai-support-bot \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator="type=nvidia-tesla-t4,count=1" \
  --image-family=debian-11-gpu \
  --image-project=debian-cloud \
  --maintenance-policy=TERMINATE \
  --restart-on-failure \
  --metadata="install-nvidia-driver=true"
```

**2. Install Dependencies**
```bash
# SSH into instance
gcloud compute ssh ai-support-bot --zone=us-central1-a

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**3. Deploy Application**
```bash
# Clone repository
git clone <your-repo-url>
cd tantorinc

# Configure environment
cp env.example .env
nano .env

# Start services
docker-compose up -d
```

### RunPod

**1. Create Pod**
- Select GPU template (RTX 4090, A100, etc.)
- Choose Ubuntu 22.04 base image
- Set startup script to install Docker and start services

**2. Startup Script**
```bash
#!/bin/bash

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update
apt-get install -y nvidia-docker2
systemctl restart docker

# Clone and start application
git clone <your-repo-url>
cd tantorinc
cp env.example .env

# Start services
docker-compose up -d
```

## Configuration Options

### Database Configuration

**PostgreSQL Settings:**
```bash
# Connection string format
DATABASE_URL=postgresql://username:password@host:port/database

# Example configurations
# Local development
DATABASE_URL=postgresql://trantor:trantor_pass@localhost:5432/trantor_db

# Docker container
DATABASE_URL=postgresql://trantor:trantor_pass@db:5432/trantor_db

# Cloud database
DATABASE_URL=postgresql://user:pass@db.example.com:5432/ai_support
```

**Vector Database Optimization:**
```sql
-- Adjust index parameters based on dataset size
-- For small datasets (< 100k chunks)
CREATE INDEX documents_embedding_ivf
  ON ai.documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

-- For large datasets (> 1M chunks)
CREATE INDEX documents_embedding_ivf
  ON ai.documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 200);
```

### LLM Configuration

**Ollama Models:**
```bash
# Available models
LLM_MODEL=ollama:qwen2.5:7b-instruct      # Fast, good quality
LLM_MODEL=ollama:llama3.1:8b-instruct-q4  # Balanced performance
LLM_MODEL=ollama:qwen2.5:14b-instruct     # Higher quality, slower

# GPU layer configuration
GPU_LAYERS=0    # CPU only
GPU_LAYERS=10   # Partial GPU acceleration
GPU_LAYERS=20   # Full GPU acceleration
```

**Model Download:**
```bash
# Download model manually
docker-compose exec ollama ollama pull qwen2.5:7b-instruct

# Check available models
docker-compose exec ollama ollama list

# Remove unused models
docker-compose exec ollama ollama rm qwen2.5:7b-instruct
```

### Embedding Configuration

**Model Selection:**
```bash
# Fast, lightweight
EMBED_MODEL=BAAI/bge-small-en-v1.5

# Higher quality, slower
EMBED_MODEL=BAAI/bge-base-en-v1.5

# Multilingual support
EMBED_MODEL=BAAI/bge-m3
```

**Chunking Parameters:**
```bash
# Document chunking settings
CHUNK_SIZE=800        # Characters per chunk
CHUNK_OVERLAP=120     # Overlap between chunks

# Adjust based on document type
# Technical docs: 800-1000 characters
# General text: 500-800 characters
# Code: 1000-1500 characters
```

## Performance Tuning

### GPU Optimization

**NVIDIA Docker Configuration:**
```bash
# Check GPU availability
nvidia-smi

# Verify Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Optimize GPU memory
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=1
```

**Model Quantization:**
```bash
# Use quantized models for better performance
LLM_MODEL=ollama:qwen2.5:7b-instruct-q4
LLM_MODEL=ollama:llama3.1:8b-instruct-q4
```

### Database Optimization

**PostgreSQL Tuning:**
```bash
# Add to postgresql.conf
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

**Vector Index Tuning:**
```sql
-- Analyze table for better query planning
ANALYZE ai.documents;

-- Rebuild index if needed
REINDEX INDEX CONCURRENTLY documents_embedding_ivf;
```

## Troubleshooting

### Common Issues

**1. Docker Permission Errors**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

**2. GPU Not Detected**
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify Docker GPU runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Restart Docker service
sudo systemctl restart docker
```

**3. Database Connection Failed**
```bash
# Check database status
docker-compose exec db pg_isready -U trantor

# Verify environment variables
docker-compose exec app env | grep DATABASE

# Check database logs
docker-compose logs db
```

**4. Out of Memory**
```bash
# Reduce chunk size
export CHUNK_SIZE=500

# Limit GPU layers
export GPU_LAYERS=10

# Use smaller model
export LLM_MODEL=ollama:qwen2.5:3b-instruct
```

### Debug Commands

```bash
# Service status
docker-compose ps

# Service logs
docker-compose logs -f app
docker-compose logs -f ollama
docker-compose logs -f db

# Resource usage
docker stats

# Container shell access
docker-compose exec app bash
docker-compose exec db psql -U trantor -d trantor_db
docker-compose exec ollama ollama list
```

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U trantor

# Ollama health
docker-compose exec ollama ollama list
```

### Backup & Recovery

**Database Backup:**
```bash
# Create backup
docker-compose exec db pg_dump -U trantor trantor_db > backup.sql

# Restore backup
docker-compose exec -T db psql -U trantor trantor_db < backup.sql
```

**Model Backup:**
```bash
# Backup Ollama models
docker run --rm -v ollama_models:/root/.ollama -v $(pwd):/backup alpine tar czf /backup/ollama-models.tar.gz /root/.ollama

# Restore models
docker run --rm -v ollama_models:/root/.ollama -v $(pwd):/backup alpine tar xzf /backup/ollama-models.tar.gz -C /
```

### Updates & Upgrades

```bash
# Update application
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# Update models
docker-compose exec ollama ollama pull qwen2.5:7b-instruct

# Update base images
docker-compose pull
docker-compose up -d
```

## Security Considerations

### Environment Security

```bash
# Use strong passwords
DATABASE_PASSWORD=your_strong_password_here

# Restrict database access
# In postgresql.conf
listen_addresses = 'localhost'

# Use SSL for external connections
# ssl = on
# ssl_cert_file = 'server.crt'
# ssl_key_file = 'server.key'
```

### Network Security

```bash
# Firewall configuration
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw allow 5432/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
```

### Access Control

```bash
# API authentication (future enhancement)
# JWT tokens
# OAuth2 integration
# Rate limiting
# IP whitelisting
```

## Next Steps

After successful setup:

1. **Ingest Documents**: Upload your product documentation
2. **Test RAG**: Ask questions about your documents
3. **Test Tools**: Create and check support tickets
4. **Customize**: Adjust prompts and configurations
5. **Scale**: Optimize for your specific use case
6. **Monitor**: Set up logging and monitoring
7. **Deploy**: Move to production environment
