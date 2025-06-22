FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Set working directory
WORKDIR /app

# Install system dependencies, including Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Create directories for models
RUN mkdir -p /app/models/checkpoints /app/models/loras /app/outputs

# Copy application files
COPY handler.py .

# Set the handler
CMD ["python3", "-u", "handler.py"]