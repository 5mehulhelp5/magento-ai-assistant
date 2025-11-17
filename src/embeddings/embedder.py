import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Use today's processed folder
today = datetime.now().strftime("%Y-%m-%d")
PROCESSED_FILE = Path(f"data/processed/magento_products_cleaned.json")

EMBEDDING_DIR = Path("data/embeddings")
EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = EMBEDDING_DIR / "product_embeddings.npy"
META_FILE = EMBEDDING_DIR / "product_metadata.json"


class ProductEmbedder:

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        print(f"🧠 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def load_products(self):
        if not PROCESSED_FILE.exists():
            raise FileNotFoundError(f"❌ Missing processed products file at {PROCESSED_FILE}")

        with open(PROCESSED_FILE, "r") as f:
            return json.load(f)

    def build_text(self, p):
        """Combine product fields into a text blob for embedding."""
        parts = [
            p.get("name", ""),
            p.get("description", ""),
            p.get("features", ""),
            str(p.get("dimensions", "")),
            str(p.get("capacity", "")),
        ]
        return ". ".join([part for part in parts if part]).strip()

    def generate_embeddings(self):
        products = self.load_products()
        print(f"📦 Loaded {len(products)} products")

        texts = [self.build_text(p) for p in products]
        print("🧠 Generating embeddings...")

        embeddings = self.model.encode(texts, show_progress_bar=True)

        print("💾 Saving embeddings & metadata...")
        np.save(OUTPUT_FILE, embeddings)

        metadata = [
            {
                "product_id": p["product_id"],
                "sku": p["sku"],
                "name": p["name"],
            }
            for p in products
        ]

        with open(META_FILE, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Saved {len(products)} embeddings → {OUTPUT_FILE}")
        print(f"📘 Metadata saved to → {META_FILE}")


if __name__ == "__main__":
    embedder = ProductEmbedder()
    embedder.generate_embeddings()
