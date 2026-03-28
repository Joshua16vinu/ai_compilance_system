
from pathlib import Path

from transformers import AutoTokenizer
import re
BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR/ "embeddings" / "models" / "all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))


def sentence_token_chunking(
    text: str,
    min_tokens: int = 150,
    max_tokens: int = 250,
    overlap: int = 40
):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = tokenizer.encode(sentence, add_special_tokens=False)
        sentence_len = len(sentence_tokens)

        if current_tokens + sentence_len > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

                # overlap logic
                overlap_chunk = []
                overlap_tokens = 0

                for s in reversed(current_chunk):
                    t = tokenizer.encode(s, add_special_tokens=False)
                    overlap_tokens += len(t)
                    overlap_chunk.insert(0, s)

                    if overlap_tokens >= overlap:
                        break

                current_chunk = overlap_chunk
                current_tokens = overlap_tokens

        current_chunk.append(sentence)
        current_tokens += sentence_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks    