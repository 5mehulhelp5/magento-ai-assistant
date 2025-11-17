import json
import faiss
import numpy as np
from pathlib import Path

EMBEDDING_DIR = Path("data/embeddings")
EMBED_FILE = EMBEDDING_DIR / "product_embeddings.npy"
META_FILE = EMBEDDING_DIR / "product_metadata.json"
INDEX_FILE = EMBEDDING_DIR / "faiss_index.bin"


def load_embeddings():
    if not EMBED_FILE.exists():
        raise FileNotFoundError(f"❌ Embeddings file missing: {EMBED_FILE}")

    embeddings = np.load(EMBED_FILE)
    print(f"📦 Loaded embeddings → shape: {embeddings.shape}")
    return embeddings.astype("float32")


def load_metadata():
    if not META_FILE.exists():
        raise FileNotFoundError(f"❌ Metadata file missing: {META_FILE}")

    with open(META_FILE, "r") as f:
        metadata = json.load(f)
    print(f"📘 Loaded metadata entries: {len(metadata)}")
    return metadata


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]

    print(f"🧠 Creating FAISS index (dimension={dim})")

    index = faiss.IndexFlatIP(dim)  # Inner product (cosine similarity with normalized vectors)

    # Normalize to use cosine similarity
    faiss.normalize_L2(embeddings)

    index.add(embeddings)

    print(f"✅ Added {index.ntotal} vectors to the FAISS index")
    return index


def save_index(index):
    faiss.write_index(index, str(INDEX_FILE))
    print(f"💾 FAISS index saved → {INDEX_FILE}")


def main():
    print("🚀 Building FAISS index...")
    
    embeddings = load_embeddings()
    metadata = load_metadata()
    
    index = build_faiss_index(embeddings)
    save_index(index)

    print("🎉 FAISS index creation complete!")


if __name__ == "__main__":
    main()
