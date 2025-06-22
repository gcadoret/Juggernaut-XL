# PowerShell Build and Deploy Script for RunPod Serverless Endpoint
# Run this from PowerShell in the directory containing your Dockerfile

# Configuration
$IMAGE_NAME = "juggernaut-xl-generator"
$TAG = "latest"
$DOCKER_USERNAME = "sampath1976"  # Replace with your Docker Hub username
$FULL_IMAGE_NAME = "$DOCKER_USERNAME/$IMAGE_NAME`:$TAG"

Write-Host "🚀 Starting build and deploy process..." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Image: $FULL_IMAGE_NAME" -ForegroundColor White
Write-Host "   Docker Version: $(docker --version)" -ForegroundColor White

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build the Docker image
Write-Host ""
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t $FULL_IMAGE_NAME .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Test the image locally (optional)
Write-Host ""
Write-Host "🧪 Testing image locally..." -ForegroundColor Yellow
$job = Start-Job -ScriptBlock { param($image) docker run --rm --gpus all -p 8080:8080 $image } -ArgumentList $FULL_IMAGE_NAME

# Wait a bit for the container to start
Start-Sleep -Seconds 10

# Kill the test container
Stop-Job $job -PassThru | Remove-Job

Write-Host "✅ Local test completed" -ForegroundColor Green

# Push to Docker Hub
Write-Host ""
Write-Host "📤 Pushing image to Docker Hub..." -ForegroundColor Yellow
Write-Host "   Please make sure you're logged in to Docker Hub:" -ForegroundColor Cyan
Write-Host "   Run: docker login" -ForegroundColor White

$response = Read-Host "Are you logged in to Docker Hub? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    docker push $FULL_IMAGE_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Image pushed successfully to Docker Hub" -ForegroundColor Green
        Write-Host "🎉 Your image is now available at: $FULL_IMAGE_NAME" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next steps:" -ForegroundColor Cyan
        Write-Host "   1. Go to RunPod Console: https://www.runpod.io/console/serverless" -ForegroundColor White
        Write-Host "   2. Create a new serverless endpoint" -ForegroundColor White
        Write-Host "   3. Use this image: $FULL_IMAGE_NAME" -ForegroundColor White
        Write-Host "   4. Set environment variables if needed" -ForegroundColor White
        Write-Host "   5. Configure your endpoint settings" -ForegroundColor White
        Write-Host ""
        Write-Host "🧪 Test your endpoint with this JSON:" -ForegroundColor Cyan
        Write-Host @"
{
  "input": {
    "prompt": "a beautiful landscape, cinematic lighting, highly detailed",
    "width": 1024,
    "height": 1024,
    "steps": 30,
    "guidance_scale": 7.5
  }
}
"@ -ForegroundColor White
    } else {
        Write-Host "❌ Failed to push image to Docker Hub" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Skipping Docker Hub push. Please login and push manually:" -ForegroundColor Yellow
    Write-Host "   docker login" -ForegroundColor White
    Write-Host "   docker push $FULL_IMAGE_NAME" -ForegroundColor White
}

Write-Host ""
Write-Host "🎯 Build and deploy process completed!" -ForegroundColor Green