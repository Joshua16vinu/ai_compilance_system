from pathlib import Path
from sentence_transformers import SentenceTransformer

_embedder = None
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "backend" / "embeddings" / "models" / "all-MiniLM-L6-v2"
def load_embedding_model():
    global _embedder

    if _embedder is None:
        _embedder = SentenceTransformer(str(MODEL_PATH))

    return _embedder

