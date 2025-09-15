# Production Dockerfile for MedGemma CAG Service
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY sankalp/ ./sankalp/
COPY .env .env

# Create model cache directory
RUN mkdir -p /app/models

# Download model during build (optional - can also be done at runtime)
# ARG HF_TOKEN
# ENV HF_TOKEN=${HF_TOKEN}
# RUN python3 -c "
# import os
# from pathlib import Path
# from huggingface_hub import snapshot_download
# 
# snapshot_download(
#     repo_id='google/medgemma-4b-it',
#     local_dir='/app/models/google--medgemma-4b-it',
#     token=os.getenv('HF_TOKEN'),
#     local_dir_use_symlinks=False,
#     ignore_patterns=['*.md', '*.txt']
# )
# "

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python3", "-m", "uvicorn", "sankalp.api:app", "--host", "0.0.0.0", "--port", "8000"]
