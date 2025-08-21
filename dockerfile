FROM nvidia/cuda:11.8.0-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

WORKDIR /app

# Install system dependencies and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install torch with correct CUDA version
RUN pip3 install --no-cache-dir torch==2.1.0+cu118 torchvision --index-url https://download.pytorch.org/whl/cu118

# Copy requirements + install the rest
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Prepare folders
RUN mkdir -p /app/models/checkpoints /app/models/loras /app/outputs

# Copy app
COPY handler.py .

# Start script with visible output
CMD ["sh", "-c", "echo 'Starting handler...' && python3 -u handler.py"]