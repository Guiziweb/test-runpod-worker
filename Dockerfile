# Use RunPod's PyTorch base image with CUDA support
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for RunPod
RUN pip install --no-cache-dir runpod

# Clone WAN 2.1 repository
RUN git clone https://github.com/Wan-Video/Wan2.1.git /app/Wan2.1

# Set WAN working directory
WORKDIR /app/Wan2.1

# Install WAN 2.1 requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for model download
RUN pip install --no-cache-dir "huggingface_hub[cli]"

# Download WAN 2.1 T2V-1.3B model (this will take a while but happens at build time)
RUN huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir ./Wan2.1-T2V-1.3B

# Copy our custom handler
COPY handler.py /app/handler.py
COPY requirements.txt /app/requirements.txt

# Install any additional requirements for our handler
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH="/app:/app/Wan2.1"
ENV MODEL_PATH="/app/Wan2.1/Wan2.1-T2V-1.3B"
ENV TORCH_DTYPE="float16"
ENV CUDA_VISIBLE_DEVICES="0"

# Expose port for RunPod
EXPOSE 8080

# Start the RunPod handler
CMD ["python", "/app/handler.py"]