import json
import faiss
import numpy as np
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer

# File locations
EMBED_DIR = Path("data/embeddings")
INDEX_FILE = EMBED_DIR / "faiss_index.bin"
META_FILE = EMBED_DIR / "product_metadata.json"

# Latest processed cleaned data
LATEST_CLEAN = Path("data/processed") / "clean_products.json"


def load_latest_products():
    if not LATEST_CLEAN.exists():
        raise FileNotFoundError(f"❌ Clean products not found at: {LATEST_CLEAN}")

    with open(LATEST_CLEAN, "r") as f:
        return json.load(f)


def build_text(product):
    """Convert product fields into a search text block."""
    parts = [
        product.get("name", ""),
        product.get("description", ""),
        product.get("features", "")
    ]
    return ". ".join([p for p in parts if p]).strip()


def refresh_faiss_index(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    print("🔄 Loading existing FAISS index and metadata...")
    index = faiss.read_index(str(INDEX_FILE))

    with open(META_FILE, "r") as f:
        old_meta = json.load(f)

    old_skus = {item["sku"] for item in old_meta}
    print(f"📘 Existing metadata: {len(old_skus)} SKUs")

    print("📦 Loading latest cleaned products...")
    products = load_latest_products()

    # Identify NEW or UPDATED products
    new_products = []
    for p in products:
        if p["sku"] not in old_skus:
            new_products.append(p)

    print(f"🆕 Found {len(new_products)} new products to index")

    if not new_products:
        print("✨ No new products. Index is already up-to-date.")
        return

    # Load the embedding model
    print("🧠 Loading embedding model for new items...")
    model = SentenceTransformer(model_name)

    # Build texts and compute embeddings
    texts = [build_text(p) for p in new_products]
    print("🔢 Generating embeddings for new items...")
    new_vecs = model.encode(texts, convert_to_tensor=False)
    new_vecs = np.asarray(new_vecs).astype("float32")

    # Normalize vectors (cosine similarity)
    faiss.normalize_L2(new_vecs)

    print(f"➕ Adding {len(new_vecs)} vectors to the index...")
    index.add(new_vecs)

    # Update metadata
    print("📘 Updating metadata file...")
    for p in new_products:
        old_meta.append({
            "sku": p["sku"],
            "name": p["name"]
        })

    # Save updated FAISS index
    faiss.write_index(index, str(INDEX_FILE))
    print(f"💾 Updated FAISS index saved → {INDEX_FILE}")

    # Save updated metadata
    with open(META_FILE, "w") as f:
        json.dump(old_meta, f, indent=2)
    print(f"💾 Metadata updated → {META_FILE}")

    print("🎉 Index refresh complete!")


if __name__ == "__main__":
    refresh_faiss_index()
