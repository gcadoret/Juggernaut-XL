# Juggernaut XL RunPod Serverless Endpoint

A RunPod serverless endpoint for generating high-quality images using the Juggernaut XL model with LoRA support.

## Features

- 🚀 **Serverless**: Deploy as a RunPod serverless endpoint
- 🎨 **High Quality**: Uses Juggernaut XL model for superior image generation
- 🔧 **LoRA Support**: Includes JuggerCineXL2 LoRA for enhanced cinematic results
- 💾 **Persistent Storage**: Models stored on RunPod network volume for fast loading
- 🛡️ **Robust Error Handling**: Graceful fallbacks and comprehensive error handling
- ⚡ **Optimized**: Memory-efficient attention and VAE slicing

## Setup

### Prerequisites

- RunPod account with GPU credits
- Hugging Face token (for model access)

### Environment Variables

Set the following environment variable in your RunPod endpoint:

- `HF_TOKEN`: Your Hugging Face token for accessing the models

### Model Files

The endpoint automatically downloads these models to the network volume:

- **Checkpoint**: `juggernautXL_juggXILightning.safetensors`
- **LoRA**: `JuggerCineXL2.safetensors`

## Usage

### API Endpoint

Send POST requests to your RunPod endpoint with the following parameters:

```json
{
  "prompt": "A beautiful landscape with mountains and sunset",
  "negative_prompt": "blurry, low quality",
  "width": 1024,
  "height": 1024,
  "steps": 30,
  "guidance_scale": 7.5,
  "seed": 42
}
```

### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `prompt` | string | - | Required | Text description of the image to generate |
| `negative_prompt` | string | "" | Optional | Text to avoid in the generated image |
| `width` | integer | 1024 | 512-1536 | Image width (must be multiple of 8) |
| `height` | integer | 1024 | 512-1536 | Image height (must be multiple of 8) |
| `steps` | integer | 30 | 10-50 | Number of denoising steps |
| `guidance_scale` | float | 7.5 | 1.0-20.0 | How closely to follow the prompt |
| `seed` | integer | null | Optional | Random seed for reproducible results |

### Response

```json
{
  "status": "success",
  "image": "base64_encoded_image_data",
  "seed": 42
}
```

## Error Handling

The endpoint includes comprehensive error handling:

- **Model Loading**: Graceful fallback if LoRA fails to load
- **Device Detection**: Works on both CUDA and CPU
- **Input Validation**: Parameter clamping and validation
- **Network Issues**: Retry logic for model downloads

## Deployment

1. Create a new RunPod serverless endpoint
2. Upload the `handler.py` file
3. Set the `HF_TOKEN` environment variable
4. Deploy with GPU support (recommended: RTX 4090 or better)

## Performance

- **First Request**: ~30-60 seconds (model loading)
- **Subsequent Requests**: ~10-30 seconds (depending on parameters)
- **Memory Usage**: ~8-12GB VRAM
- **Supported Resolutions**: 512x512 to 1536x1536

## Troubleshooting

### Common Issues

1. **"HF_TOKEN not found"**: Set the environment variable in RunPod
2. **"Failed to load LoRA"**: The endpoint will continue without LoRA
3. **"CUDA out of memory"**: Reduce image resolution or steps
4. **"Model download failed"**: Check network connectivity and HF_TOKEN

### Logs

Check the RunPod logs for detailed error messages and progress information.

## License

This project uses the Juggernaut XL model which is subject to its own license terms.

## Contributing

Feel free to submit issues and enhancement requests! 