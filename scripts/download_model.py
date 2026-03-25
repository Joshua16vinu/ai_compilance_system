# download_q5.py
import requests
import os
from tqdm import tqdm

# Q5_K_M (5.1GB)
MODEL_URL = "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q5_K_M.gguf"
MODEL_FILE = "models/Mistral-7B-Instruct-v0.3-Q5_K_M.gguf"
#hello
os.makedirs("models", exist_ok=True)

print("Downloading Q5_K_M (5GB)...")
response = requests.get(MODEL_URL, stream=True)
total = int(response.headers.get('content-length', 0))

with open(MODEL_FILE, 'wb') as f, tqdm(
    desc=MODEL_FILE,
    total=total,
    unit='iB',
    unit_scale=True,
    unit_divisor=1024,
) as bar:
    for data in response.iter_content(chunk_size=1024):
        size = f.write(data)
        bar.update(size)
#hkdf
print(f"✅ Saved: {MODEL_FILE}")