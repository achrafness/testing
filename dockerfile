# Use a PyTorch image with CUDA 11.7 and cuDNN8 runtime support
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
# Optionally disable AO quantization (may help with older torch versions)
ENV DIFFUSERS_NO_TORCH_AO_QUANTIZATION=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install pip requirements and then upgrade torch to 2.1.0
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install torch==2.1.0

# Clone cog-sdxl (since it isn’t pip-installable) and add it to PYTHONPATH
RUN git clone https://github.com/replicate/cog-sdxl.git
ENV PYTHONPATH="/app/cog-sdxl:${PYTHONPATH}"

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]

