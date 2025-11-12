import json
from datetime import datetime
from pathlib import Path
from .clean.cleaners import clean_text
from .clean.transformers import map_product_attributes

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_product(p):
    mapped = map_product_attributes(p)

    return {
        "sku": p.get("sku"),
        "name": clean_text(p.get("name", "")),
        "description": clean_text(mapped["description"]),
        "features": clean_text(mapped["features"]),
        "material": "aluminium" if "aluminium" in p.get("name", "").lower() else None,
        "length_mm": int(mapped["length"]) if mapped["length"] and str(mapped["length"]).isdigit() else None,
        "weight_kg": p.get("weight"),
        "corrosion_resistant": mapped["corrosion"],
        "uom": mapped["uom"],
        "country_of_manufacture": mapped["country"],
        "category_id": mapped["category_ids"][0] if isinstance(mapped["category_ids"], list) and mapped["category_ids"] else None,
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
    cleaned = [clean_product(item) for item in items]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2 , ensure_ascii=False)

    print(f"✅ Cleaned {len(cleaned)} products → saved to {output_file}")

if __name__ == "__main__":
    preprocess_all()
