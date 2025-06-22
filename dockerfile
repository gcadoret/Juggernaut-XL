FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    diffusers==0.24.0 \
    transformers==4.36.0 \
    accelerate==0.25.0 \
    torch==2.1.0 \
    torchvision==0.16.0 \
    xformers==0.0.22.post7 \
    runpod==1.5.1 \
    requests==2.31.0 \
    Pillow==10.1.0 \
    safetensors==0.4.1 \
    compel==2.0.2

# Create directories for models
RUN mkdir -p /app/models/checkpoints /app/models/loras /app/outputs

# Copy application files
COPY handler.py /app/

# Set the handler
CMD ["python", "-u", "handler.py"]