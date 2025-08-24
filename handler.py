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
        # Prepare WAN 2.1 command
        cmd = [
            "python", "/app/Wan2.1/generate.py",
            "--task", "t2v-1.3B",
            "--size", "832*480",
            "--ckpt_dir", "/app/Wan2.1/Wan2.1-T2V-1.3B",
            "--offload_model", "True",
            "--t5_cpu",
            "--sample_shift", "8", 
            "--sample_guide_scale", "6",
            "--prompt", prompt,
            "--output_dir", os.path.dirname(output_path)
        ]
        
        print(f"Executing WAN 2.1 generation with prompt: {prompt}")
        print(f"Command: {' '.join(cmd)}")
        
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

def upload_to_storage(video_path: str) -> str:
    """
    Upload video to storage and return public URL
    For now, we'll simulate this with a temporary URL
    In production, you'd upload to S3, GCS, or similar
    """
    # Generate unique filename
    video_id = f"wan_{uuid.uuid4().hex[:8]}_{int(time.time())}"
    
    # For now, return a mock URL - in production you'd upload to real storage
    # Example S3 upload:
    # import boto3
    # s3 = boto3.client('s3')
    # bucket = 'your-video-bucket'
    # key = f'videos/{video_id}.mp4'
    # s3.upload_file(video_path, bucket, key)
    # return f'https://{bucket}.s3.amazonaws.com/{key}'
    
    return f"https://storage.runpod.io/wan-videos/{video_id}.mp4"

def handler(job):
    """
    RunPod serverless handler for WAN 2.1 video generation
    """
    print("WAN 2.1 video generation handler started")
    
    # Get input from job
    job_input = job.get("input", {})
    
    # Validate input
    schema = {
        "prompt": {
            "type": str,
            "required": True,
            "constraints": lambda x: len(x.strip()) > 0 and len(x) <= 500
        }
    }
    
    try:
        validated_input = validate(job_input, schema)
        prompt = validated_input.get("prompt")
    except Exception as e:
        return {"error": f"Input validation failed: {str(e)}"}
    
    print(f"Generating video for prompt: {prompt}")
    
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
        
        # Upload to storage
        video_url = upload_to_storage(video_path)
        
        # Clean up temporary files
        try:
            os.remove(video_path)
            os.rmdir(temp_dir)
        except:
            pass  # Don't fail if cleanup fails
        
        # Return success response
        return {
            "video_url": video_url,
            "prompt": prompt,
            "model": "wan-2.1-t2v-1.3b",
            "resolution": "832x480",
            "duration_seconds": 5
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {"error": f"Video generation failed: {str(e)}"}

if __name__ == "__main__":
    print("Starting WAN 2.1 RunPod serverless worker...")
    runpod.serverless.start({"handler": handler})