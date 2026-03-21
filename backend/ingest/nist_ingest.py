import sys
import os
import json
import chromadb
from pathlib import Path
from chromadb import PersistentClient   

# Ensure project root is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.embeddings.embedding_model import load_embedding_model

# -------- Paths (SAFE & CORRECT) --------
BASE_DIR = Path(__file__).resolve().parents[2]

JSON_PATH = BASE_DIR / "backend" / "data" / "chunks_of_nist.json"
DB_PATH = BASE_DIR / "backend" / "db" / "chroma"

COLLECTION_NAME = "nist_controls"

# -------- Safety check --------
if DB_PATH.exists() and any(DB_PATH.iterdir()):
    print("✅ ChromaDB already exists. Skipping ingestion.")
    exit()

# -------- Load JSON --------
print("🔄 Loading JSON...")
with open(JSON_PATH, "r", encoding="utf-8") as f:
    nist_data = json.load(f)

# -------- Load embedding model --------
print("🔄 Loading embedding model...")
embedder = load_embedding_model()

# -------- Init ChromaDB --------
print("🔄 Initializing ChromaDB...")
client = PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(name=COLLECTION_NAME)

# -------- Embed & store --------
print("🔄 Creating embeddings and storing...")
for item in nist_data:
    embedding = embedder.encode(item["text"]).tolist()

    collection.add(
        ids=[item["id"]],
        documents=[item["text"]],
        metadatas=[{
            "domain": item.get("domain"),
            "subdomain": item.get("subdomain"),
            "source": item.get("source")
        }],
        embeddings=[embedding]
    )

print("✅ NIST embeddings stored successfully.")
