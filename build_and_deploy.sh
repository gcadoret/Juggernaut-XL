#!/bin/bash

# Build and Deploy Script for RunPod Serverless Endpoint
# Make sure to run this from the directory containing your Dockerfile

set -e  # Exit on any error

echo "🚀 Starting build and deploy process..."

# Configuration
IMAGE_NAME="juggernaut-xl-generator"
TAG="latest"
DOCKER_USERNAME="sampath1976"  # Replace with your Docker Hub username

# Ensure repository name follows Docker Hub rules (lowercase, alphanumeric, ., _, -)
IMAGE_NAME=$(echo "$IMAGE_NAME" | tr '[:upper:]' '[:lower:]')
DOCKER_USERNAME=$(echo "$DOCKER_USERNAME" | tr '[:upper:]' '[:lower:]')
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "📋 Configuration:"
echo "   Image: ${FULL_IMAGE_NAME}"
echo "   Docker Desktop: $(docker --version)"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Test the image locally (optional)
echo "🧪 Testing image locally..."
docker run --rm --gpus all -p 8080:8080 ${FULL_IMAGE_NAME} &
CONTAINER_PID=$!

# Wait a bit for the container to start
sleep 10

# Kill the test container
kill $CONTAINER_PID 2>/dev/null || true

echo "✅ Local test completed"

# Push to Docker Hub
echo "📤 Pushing image to Docker Hub..."
echo "   Please make sure you're logged in to Docker Hub:"
echo "   Run: docker login"

read -p "Are you logged in to Docker Hub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push ${FULL_IMAGE_NAME}
    
    if [ $? -eq 0 ]; then
        echo "✅ Image pushed successfully to Docker Hub"
        echo "🎉 Your image is now available at: ${FULL_IMAGE_NAME}"
        echo ""
        echo "📝 Next steps:"
        echo "   1. Go to RunPod Console: https://www.runpod.io/console/serverless"
        echo "   2. Create a new serverless endpoint"
        echo "   3. Use this image: ${FULL_IMAGE_NAME}"
        echo "   4. Set environment variables if needed"
        echo "   5. Configure your endpoint settings"
        echo ""
        echo "🧪 Test your endpoint with this JSON:"
        echo '{'
        echo '  "input": {'
        echo '    "prompt": "a beautiful landscape, cinematic lighting, highly detailed",'
        echo '    "width": 1024,'
        echo '    "height": 1024,'
        echo '    "steps": 30,'
        echo '    "guidance_scale": 7.5'
        echo '  }'
        echo '}'
    else
        echo "❌ Failed to push image to Docker Hub"
        exit 1
    fi
else
    echo "⚠️  Skipping Docker Hub push. Please login and push manually:"
    echo "   docker login"
    echo "   docker push ${FULL_IMAGE_NAME}"
fi

echo "🎯 Build and deploy process completed!"