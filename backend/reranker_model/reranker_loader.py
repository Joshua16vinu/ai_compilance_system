from pathlib import Path
from sentence_transformers import CrossEncoder

_reranker = None

BASE_DIR = Path(__file__).resolve().parents[2]
RERANKER_PATH = BASE_DIR / "backend" / "reranker_model" / "models" / "cross-encoder-ms-marco-MiniLM-L-6-v2"

def load_reranker():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(str(RERANKER_PATH))

    return _reranker