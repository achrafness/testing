from flask import Flask, request, jsonify
import torch
from diffusers import DiffusionPipeline
from huggingface_hub import hf_hub_download
from cog_sdxl.dataset_and_utils import TokenEmbeddingsHandler
from io import BytesIO
import base64
from PIL import Image

app = Flask(__name__)

# Use CUDA if available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the base Stable Diffusion XL model
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    variant="fp16" if device == "cuda" else None,
).to(device)

# Load the LoRA weights from fofr/sdxl-emoji
pipe.load_lora_weights("fofr/sdxl-emoji", weight_name="lora.safetensors")

# Load the trigger token embeddings
text_encoders = [pipe.text_encoder, pipe.text_encoder_2]
tokenizers = [pipe.tokenizer, pipe.tokenizer_2]
embedding_path = hf_hub_download(
    repo_id="fofr/sdxl-emoji", filename="embeddings.pti", repo_type="model"
)
embhandler = TokenEmbeddingsHandler(text_encoders, tokenizers)
embhandler.load_embeddings(embedding_path)

@app.route("/generate", methods=["POST"])
def generate_avatar():
    data = request.get_json()
    # Use a default prompt if none provided
    prompt = data.get("prompt", "emoji of a man")
    full_prompt = f"A <s0><s1> {prompt}"
    
    # Generate image using autocast for performance
    with torch.autocast(device):
        output = pipe(full_prompt, cross_attention_kwargs={"scale": 0.8})
    
    image = output.images[0]
    
    # Save the image to an in-memory buffer and encode in base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return jsonify({"image": img_str})

if __name__ == "__main__":
    # Run the Flask app on port 5000, accessible on all interfaces
    app.run(host="0.0.0.0", port=5000)

