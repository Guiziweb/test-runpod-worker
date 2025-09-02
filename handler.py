import runpod
import os
import sys
import subprocess
import uuid
import time
import json
from pathlib import Path

# Add WAN2.1 to Python path
sys.path.append('/app/Wan2.1')

# Import WAN validation
try:
    from runpod.serverless.utils.rp_validator import validate
except ImportError:
    print("RunPod validator not available, using basic validation")
    def validate(job_input, schema):
        return job_input

def generate_video_with_wan(prompt: str, output_path: str) -> bool:
    """
    Generate video using WAN 2.1 T2V-1.3B model
    
    Args:
        prompt: Text description for video generation
        output_path: Path where to save the generated video
        
    Returns:
        bool: True if generation successful, False otherwise
    """
    try:
        # Validate prompt is a string before using it
        if not isinstance(prompt, str):
            raise ValueError(f"Prompt must be a string, got {type(prompt)}")
            
        # Prepare WAN 2.1 command
        cmd = [
            "python", "/app/Wan2.1/generate.py",
            "--task", "t2v-1.3B",
            "--size", "832*480",
            "--ckpt_dir", "/app/Wan2.1/Wan2.1-T2V-1.3B",
            "--offload_model",
            "--t5_cpu",
            "--sample_shift", "8", 
            "--sample_guide_scale", "6",
            "--prompt", str(prompt),  # Ensure it's a string
            "--output_dir", os.path.dirname(output_path)
        ]
        
        print(f"Executing WAN 2.1 generation with prompt: {prompt}")
        print(f"Command: {' '.join(str(arg) for arg in cmd)}")  # Convert all to string for join
        
        # Execute WAN generation
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
        
        if result.returncode == 0:
            print("WAN 2.1 generation completed successfully")
            print(f"stdout: {result.stdout}")
            
            # WAN generates files in output_dir, find the generated video
            output_dir = os.path.dirname(output_path)
            generated_files = list(Path(output_dir).glob("*.mp4"))
            
            if generated_files:
                # Move the first generated video to our expected path
                generated_file = generated_files[0]
                os.rename(str(generated_file), output_path)
                print(f"Video saved to: {output_path}")
                return True
            else:
                print("No video files found after generation")
                return False
        else:
            print(f"WAN 2.1 generation failed with return code: {result.returncode}")
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("WAN 2.1 generation timed out (10 minutes)")
        return False
    except Exception as e:
        print(f"Error during WAN 2.1 generation: {str(e)}")
        return False

def encode_video_base64(video_path: str) -> str:
    """
    Encode video as base64 for direct return
    """
    import base64
    
    with open(video_path, 'rb') as f:
        video_data = f.read()
    
    # Encode to base64
    base64_data = base64.b64encode(video_data).decode('utf-8')
    
    print(f"Video size: {len(video_data)} bytes, base64 size: {len(base64_data)} bytes")
    
    return f"data:video/mp4;base64,{base64_data}"

def handler(job):
    """
    RunPod serverless handler for WAN 2.1 video generation
    """
    print("WAN 2.1 video generation handler started")
    
    # Get input from job
    job_input = job.get("input", {})
    print(f"Received job input: {job_input}")
    
    # Simple validation - RunPod's validate might not work as expected
    prompt = job_input.get("prompt")
    
    # Check if prompt exists and is valid
    if not prompt:
        error_msg = "Missing required field: prompt"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    if not isinstance(prompt, str):
        error_msg = f"Prompt must be a string, got {type(prompt).__name__}"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    prompt = prompt.strip()
    if len(prompt) == 0:
        error_msg = "Prompt cannot be empty"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    if len(prompt) > 500:
        error_msg = "Prompt too long (max 500 characters)"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    print(f"Validated prompt: {prompt}")
    
    # Create temporary directory for generation
    temp_dir = f"/tmp/wan_generation_{uuid.uuid4().hex[:8]}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate output path
    video_path = os.path.join(temp_dir, "generated_video.mp4")
    
    try:
        # Generate video with WAN 2.1
        success = generate_video_with_wan(prompt, video_path)
        
        if not success:
            return {"error": "Video generation failed"}
        
        # Check if video file exists and has content
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            return {"error": "Generated video file is missing or empty"}
        
        # For RunPod, it's better to upload to their storage
        # But for now, we'll use base64 with size check
        video_size = os.path.getsize(video_path)
        print(f"Generated video size: {video_size} bytes")
        
        # RunPod has response size limits, check if video is too large
        if video_size > 50 * 1024 * 1024:  # 50MB limit
            return {"error": f"Video too large ({video_size} bytes). Max 50MB for base64 response."}
        
        # Encode video as base64
        video_url = encode_video_base64(video_path)
        
        # Clean up temporary files
        try:
            os.remove(video_path)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Cleanup warning: {e}")
        
        # Return success response
        return {
            "video_url": video_url,
            "prompt": prompt,
            "model": "wan-2.1-t2v-1.3b",
            "resolution": "832x480",
            "duration_seconds": 5,
            "size_bytes": video_size
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {"error": f"Video generation failed: {str(e)}"}

if __name__ == "__main__":
    print("Starting WAN 2.1 RunPod serverless worker...")
    runpod.serverless.start({"handler": handler})