import json
from datetime import datetime
from pathlib import Path
from .clean.cleaners import clean_text, flatten_products, normalize_capacity, normalize_dimensions
from .clean.transformers import map_product_attributes
from typing import Dict, Any

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)  # Ensure folder exists

def clean_product(p: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced cleaning with propagation-aware extraction."""
    mapped = map_product_attributes(p)  # Existing transformer

    # Extract with fallbacks
    full_text = f"{mapped.get('description', '')} {mapped.get('features', '')} {p.get('name', '')}"
    dimensions = normalize_dimensions(full_text, p.get("sku", ""), p.get("name", ""))
    capacity = normalize_capacity(full_text) or normalize_capacity(mapped.get("description", ""))

    return {
        "sku": p.get("sku"),
        "name": clean_text(p.get("name", "")),
        "description": clean_text(mapped.get("description", "")),
        "features": clean_text(mapped.get("features", "")),
        "material": mapped.get("material", "aluminium" if "aluminium" in p.get("name", "").lower() else None),
        "length_mm": int(mapped.get("length")) if mapped.get("length") and str(mapped.get("length")).isdigit() else None,
        "dimensions": dimensions,
        "capacity": capacity,
        "weight_kg": p.get("weight"),
        "corrosion_resistant": mapped.get("corrosion_resistant", False),
        "uom": mapped.get("uom"),
        "country_of_manufacture": mapped.get("country_of_manufacture"),
        "category_id": mapped.get("category_ids")[0] if isinstance(mapped.get("category_ids"), list) and mapped.get("category_ids") else None,
        "timestamp": datetime.utcnow().isoformat()
    }

def preprocess_all():
    input_file = RAW_DIR / "magento_products_full.json"
    output_file = PROCESSED_DIR / "clean_products.json"

    if not input_file.exists():
        print(f"❌ No raw data found at {input_file}")
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    items = data.get("items", []) if isinstance(data, dict) else data
    flattened_items = flatten_products(items)
    cleaned = [clean_product(item) for item in flattened_items]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2 , ensure_ascii=False)

    print(f"✅ Cleaned {len(cleaned)} products → saved to {output_file}")

if __name__ == "__main__":
    preprocess_all()
