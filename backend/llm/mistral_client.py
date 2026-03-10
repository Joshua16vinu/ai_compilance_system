from llama_cpp import Llama
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "phi-3-mini-4k-instruct-q4_k_m.gguf"

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,            # context window
    n_threads=os.cpu_count(),           # adjust to your CPU cores
    n_gpu_layers=0,        # set >0 only if CUDA build is available
    verbose=False
)

def call_llm(prompt: str) -> str:
    response = llm(
        prompt,
        max_tokens=800,
        temperature=0.0,
        stop=["</s>"]        # important for Mistral
    )
    return response["choices"][0]["text"].strip()
