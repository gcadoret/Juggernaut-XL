import requests
import json
import base64
from PIL import Image
import io
import time

class RunPodClient:
    def __init__(self, endpoint_id, api_key):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt, **kwargs):
        """Generate an image using the RunPod endpoint"""
        
        # Prepare the request payload
        payload = {
            "input": {
                "prompt": prompt,
                "negative_prompt": kwargs.get("negative_prompt", ""),
                "width": kwargs.get("width", 1024),
                "height": kwargs.get("height", 1024),
                "steps": kwargs.get("steps", 30),
                "guidance_scale": kwargs.get("guidance_scale", 7.5),
                "seed": kwargs.get("seed", None)
            }
        }
        
        print(f"🎨 Generating image: {prompt[:50]}...")
        print(f"📊 Parameters: {payload['input']}")
        
        try:
            # Submit the job
            response = requests.post(
                f"{self.base_url}/run",
                headers=self.headers,
                json=payload,
                timeout=300
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "id" in result:
                job_id = result["id"]
                print(f"📋 Job submitted with ID: {job_id}")
                
                # Poll for results
                return self.wait_for_result(job_id)
            else:
                print("❌ Failed to submit job")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def wait_for_result(self, job_id, max_wait=300):
        """Wait for job completion and return result"""
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/status/{job_id}",
                    headers=self.headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status", "UNKNOWN")
                print(f"⏳ Status: {status}")
                
                if status == "COMPLETED":
                    output = result.get("output", {})
                    if output.get("status") == "success":
                        print("✅ Image generated successfully!")
                        return output
                    else:
                        print(f"❌ Generation failed: {output.get('message', 'Unknown error')}")
                        return None
                        
                elif status == "FAILED":
                    error = result.get("error", "Unknown error")
                    print(f"❌ Job failed: {error}")
                    return None
                
                elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                    time.sleep(5)  # Wait 5 seconds before checking again
                    continue
                else:
                    print(f"⚠️ Unknown status: {status}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error checking status: {str(e)}")
                time.sleep(5)
        
        print("⏰ Timeout waiting for result")
        return None
    
    def save_image(self, output, filename="generated_image.png"):
        """Save the generated image to file"""
        
        if not output or "image" not in output:
            print("❌ No image data in output")
            return False
        
        try:
            # Decode base64 image
            image_data = base64.b64decode(output["image"])
            image = Image.open(io.BytesIO(image_data))
            
            # Save image
            image.save(filename)
            print(f"💾 Image saved as {filename}")
            print(f"📏 Image size: {image.size}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving image: {str(e)}")
            return False

def main():
    # Configuration - Replace with your actual values
    ENDPOINT_ID = "your-endpoint-id-here"  # Replace with your RunPod endpoint ID
    API_KEY = "your-api-key-here"          # Replace with your RunPod API key
    
    if ENDPOINT_ID == "your-endpoint-id-here" or API_KEY == "your-api-key-here":
        print("⚠️  Please update the ENDPOINT_ID and API_KEY in the script")
        print("   You can find these in your RunPod console")
        return
    
    # Initialize client
    client = RunPodClient(ENDPOINT_ID, API_KEY)
    
    # Test prompts
    test_cases = [
        {
            "prompt": "a majestic dragon flying over a medieval castle, cinematic lighting, highly detailed, fantasy art",
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "guidance_scale": 7.5
        },
        {
            "prompt": "a futuristic cyberpunk city at night, neon lights, rain, atmospheric",
            "width": 1024,
            "height": 768,
            "steps": 25,
            "guidance_scale": 8.0,
            "negative_prompt": "blurry, low quality, distorted"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"🧪 Test Case {i+1}")
        print(f"{'='*60}")
        
        # Generate image
        result = client.generate_image(**test_case)
        
        if result:
            # Save image
            filename = f"test_image_{i+1}.png"
            client.save_image(result, filename)
            
            # Print seed if available
            if "seed" in result and result["seed"]:
                print(f"🌱 Seed: {result['seed']}")
        
        print(f"✅ Test case {i+1} completed\n")
    
    print("🎉 All tests completed!")

# Example usage for single image generation
def generate_single_image():
    """Example function for generating a single image"""
    
    # Replace with your credentials
    ENDPOINT_ID = "your-endpoint-id-here"
    API_KEY = "your-api-key-here"
    
    client = RunPodClient(ENDPOINT_ID, API_KEY)
    
    result = client.generate_image(
        prompt="a beautiful sunset over the ocean, cinematic, highly detailed",
        width=1024,
        height=1024,
        steps=30,
        guidance_scale=7.5,
        negative_prompt="blurry, low quality"
    )
    
    if result:
        client.save_image(result, "sunset.png")

if __name__ == "__main__":
    main()