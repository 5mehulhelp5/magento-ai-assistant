import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import argparse
from src.utils.magento_client import MagentoClient  # For API access
from .save_processor import save_to_formats, embed_keys_and_timestamps  # For persistence

client = MagentoClient()
SYNC_CONFIG_PATH = Path("data/sync_config.json")  # JSON for robustness

def get_last_sync_date():
    """Retrieve last sync date from JSON config."""
    if SYNC_CONFIG_PATH.exists():
        with open(SYNC_CONFIG_PATH, "r") as f:
            config = json.load(f)
            return datetime.fromisoformat(config.get('last_sync_date', '1970-01-01T00:00:00'))
    return datetime(1970, 1, 1)

def update_last_sync_date(date: datetime):
    """Update sync date in JSON config."""
    config = {'last_sync_date': date.isoformat()}
    SYNC_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Updated sync config: last_sync_date = {date.isoformat()}")

def fetch_delta_from_api(last_sync: datetime, page_size: int = 100) -> list:
    """Fetch deltas directly from Magento API."""
    all_delta = []
    page = 1
    while True:
        params = {
            "searchCriteria[currentPage]": page,
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[filterGroups][0][filters][0][field]": "updated_at",
            "searchCriteria[filterGroups][0][filters][0][condition_type]": "gt",  # Operator for > last_sync
            "searchCriteria[filterGroups][0][filters][0][value]": last_sync.isoformat() + "Z",  # UTC ISO timestamp
        }
        data = client.get("/V1/products", params=params)
        items = data.get("items", [])
        if not items:
            break
        all_delta.extend(items)
        if len(items) < page_size:
            break
        page += 1
    print(f"Fetched {len(all_delta)} delta products since {last_sync.isoformat()}")
    return all_delta

def merge_deltas(existing_df: pd.DataFrame, delta_products: list) -> pd.DataFrame:
    """Merge deltas into existing cleaned data (robust handling for overlapping columns)."""
    if not delta_products:
        return existing_df
    
    # Prepare delta DF with SKU as key
    delta_df = pd.DataFrame(delta_products)
    if 'sku' not in delta_df.columns:
        delta_df['sku'] = delta_df.get('id', range(len(delta_df))).astype(str)  # Fallback if no SKU
    delta_df.set_index('sku', inplace=True)
    
    # Prepare existing (ensure SKU index)
    if existing_df.empty:
        return delta_df.reset_index()  # First run: use deltas as base
    
    existing_df = existing_df.copy()
    if 'sku' not in existing_df.columns:
        existing_df['sku'] = existing_df['product_id']
    existing_df.set_index('sku', inplace=True)
    
    # Identify new vs. existing
    new_skus = set(delta_df.index) - set(existing_df.index)
    overlapping_skus = set(delta_df.index) & set(existing_df.index)
    
    # Append new SKUs via concat (aligns columns automatically)
    if new_skus:
        new_df = delta_df.loc[list(new_skus)]
        existing_df = pd.concat([existing_df, new_df], sort=False)  # sort=False preserves order
        print(f"Appended {len(new_skus)} new SKUs")
    
    # Update overlapping using pd.update (safe, column-aligned overwrite)
    if overlapping_skus:
        overlapping_df = delta_df.loc[list(overlapping_skus)]
        existing_df.update(overlapping_df)  # Overwrites matching columns; ignores extras
        print(f"Updated {len(overlapping_skus)} existing SKUs")
    
    return existing_df.reset_index()

def delta_sync(page_size: int = 100):
    """Full delta sync workflow."""
    last_sync = get_last_sync_date()
    delta_products = fetch_delta_from_api(last_sync, page_size=page_size)
    
    # Load existing cleaned data
    processed_dir = Path("data/processed")
    existing_csv = processed_dir / "magento_products_cleaned.csv"
    if existing_csv.exists():
        existing_df = pd.read_csv(existing_csv)
    else:
        existing_df = pd.DataFrame()
    
    merged_df = merge_deltas(existing_df, delta_products)
    
    if 'sku' not in merged_df.columns:
        if 'product_id' in merged_df.columns:
            merged_df['sku'] = merged_df['product_id']
        else:
            merged_df['sku'] = [f"SKU_{i}" for i in range(len(merged_df))]
    # Persist
    enhanced_df = embed_keys_and_timestamps(merged_df)
    save_to_formats(enhanced_df, processed_dir)
    
    # Update config (use max updated_at from deltas)
    if delta_products:
        newest = max(datetime.fromisoformat(p["updated_at"]) for p in delta_products)
        update_last_sync_date(newest)
    else:
        update_last_sync_date(datetime.utcnow())  # No-op sync

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delta Sync Manager")
    parser.add_argument('--page-size', type=int, default=100, help='API page size')
    args = parser.parse_args()
    delta_sync(page_size=args.page_size)