import os
import base64
import io
import runpod
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import json
import requests
import time
import traceback


# --- Helper Function for Downloading ---
def download_file(url, dest_path, headers=None, max_retries=3):
    """Download a file with progress, retry logic, and auth headers."""
    if os.path.exists(dest_path):
        print(f"✓ {os.path.basename(dest_path)} already exists, skipping...")
        return
        
    for attempt in range(max_retries):
        try:
            print(f"Downloading {os.path.basename(dest_path)} (attempt {attempt + 1}/{max_retries})...")
            with requests.get(url, stream=True, headers=headers, timeout=300) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                with open(dest_path, 'wb') as f:
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\rProgress: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✓ Successfully downloaded {os.path.basename(dest_path)}")
            return
            
        except Exception as e:
            print(f"\n✗ Attempt {attempt + 1} failed: {str(e)}")
            if os.path.exists(dest_path):
                os.remove(dest_path) # Clean up partial download
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Failed to download {os.path.basename(dest_path)} after {max_retries} attempts.")
                raise e

# Global pipeline variable
pipeline = None

def load_pipeline():
    """Load and initialize the pipeline, downloading models if necessary."""
    global pipeline
    
    if pipeline is not None:
        return pipeline
    
    # --- Model Configuration ---
    # IMPORTANT: The token is read from a RunPod environment variable `HF_TOKEN`
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Warning: HF_TOKEN not found. Some models may not be accessible.")
        headers = {}
    else:
        headers = {"Authorization": f"Bearer {hf_token}"}

    # Fixed URLs - checkpoint and LoRA are different files
    checkpoint_url = "https://huggingface.co/Sampath76/Juggernaut-XL/resolve/main/juggernautXL_juggXILightning.safetensors?download=true"
    lora_url = "https://huggingface.co/Sampath76/Juggernaut-XL/resolve/main/JuggerCineXL2.safetensors?download=true"
    
    # Paths for persistent network volume storage
    checkpoint_path = "/app/models/checkpoints/juggernautXL_juggXILightning.safetensors"
    lora_path = "/app/models/loras/JuggerCineXL2.safetensors"

    # --- Download Models to Persistent Volume ---
    print("Ensuring models are available on network volume...")
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    os.makedirs(os.path.dirname(lora_path), exist_ok=True)
    
    try:
        download_file(checkpoint_url, checkpoint_path, headers=headers)
        download_file(lora_url, lora_path, headers=headers)
    except Exception as e:
        print(f"Error downloading models: {str(e)}")
        raise e
    
    print("\nLoading Juggernaut XL pipeline from network volume...")
    
    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Initialize pipeline with the checkpoint
        pipeline = StableDiffusionXLPipeline.from_single_file(
            checkpoint_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )
        
        # Load LoRA weights with error handling
        if os.path.exists(lora_path):
            try:
                print("Loading LoRA weights...")
                pipeline.load_lora_weights(lora_path)
                pipeline.fuse_lora()
                print("✓ LoRA weights loaded successfully")
            except Exception as lora_error:
                print(f"Warning: Failed to load LoRA weights: {str(lora_error)}")
                print("Continuing without LoRA weights...")
        else:
            print("Warning: LoRA file not found, continuing without LoRA weights...")
        
        # Set scheduler
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config
        )
        
        # Enable memory efficient attention
        pipeline.enable_attention_slicing()
        pipeline.enable_vae_slicing()
        
        # Move to GPU
        pipeline = pipeline.to(device)
        
        print(f"Pipeline loaded successfully on {device}")
        return pipeline
        
    except Exception as e:
        print(f"Error loading pipeline: {str(e)}")
        traceback.print_exc()  # ⬅ Affiche la stack complète
        pipeline = None
        raise e

def generate_image(prompt, negative_prompt="", width=1024, height=1024, 
                  num_inference_steps=30, guidance_scale=7.5, seed=None):
    """Generate image using the pipeline"""
    
    try:
        pipeline = load_pipeline()
        
        # Set seed for reproducibility
        if seed is not None:
            torch.manual_seed(seed)
        
        print(f"Generating image: {prompt[:50]}...")
        
        # Generate image with timeout protection
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        with torch.autocast(device):
            result = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=torch.Generator().manual_seed(seed) if seed else None
            )
        
        # Get the image
        image = result.images[0]
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "seed": seed
        }
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def handler(job):
    """RunPod handler function"""
    
    try:
        # Get job input
        job_input = job.get("input", {})
        
        # Extract parameters
        prompt = job_input.get("prompt", "")
        negative_prompt = job_input.get("negative_prompt", "")
        width = job_input.get("width", 1024)
        height = job_input.get("height", 1024)
        steps = job_input.get("steps", 30)
        guidance_scale = job_input.get("guidance_scale", 7.5)
        seed = job_input.get("seed", None)
        
        # Validate input
        if not prompt:
            return {
                "error": "Prompt is required"
            }
        
        # Ensure dimensions are multiples of 8
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        # Clamp values
        width = max(512, min(1536, width))
        height = max(512, min(1536, height))
        steps = max(10, min(50, steps))
        guidance_scale = max(1.0, min(20.0, guidance_scale))
        
        print(f"Processing job with prompt: {prompt[:100]}")
        
        # Generate image
        result = generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        return result
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {
            "error": str(e)
        }

# Start the RunPod serverless handler
runpod.serverless.start({"handler": handler})