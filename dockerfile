# Use a PyTorch image with CUDA 11.7 and cuDNN8 runtime support
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Clone the cog-sdxl repository (this contains the TokenEmbeddingsHandler utility)
RUN git clone https://github.com/replicate/cog-sdxl.git

# Add the cloned cog-sdxl repository to the PYTHONPATH
ENV PYTHONPATH="/app/cog-sdxl:${PYTHONPATH}"

# Copy the Flask application code into the container
COPY . .

# Expose the Flask port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]

