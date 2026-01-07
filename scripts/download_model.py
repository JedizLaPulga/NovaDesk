from huggingface_hub import hf_hub_download
import os

def download_onnx_model():
    model_id = "Xenova/all-MiniLM-L6-v2"
    save_dir = "src/engine/model_cache"
    
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"Downloading ONNX model from {model_id} to {save_dir}...")
    
    # Xenova repo structure usually has onnx/model.onnx (quantized) or just model.onnx
    # We will try standard files.
    files_to_download = [
        "onnx/model.onnx", 
        "tokenizer.json", 
        "config.json", 
        "special_tokens_map.json",
        "tokenizer_config.json"
    ]
    
    for filename in files_to_download:
        try:
            print(f"Fetching {filename}...")
            # Using local_dir_use_symlinks=False to ensure real files for .exe bundling
            hf_hub_download(
                repo_id=model_id, 
                filename=filename, 
                local_dir=save_dir,
                local_dir_use_symlinks=False
            )
        except Exception as e:
            print(f"Warning: Could not download {filename}. Error: {e}")

if __name__ == "__main__":
    download_onnx_model()
