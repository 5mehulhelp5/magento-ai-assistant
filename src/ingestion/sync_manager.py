import json
from datetime import datetime

# Example: last sync stored in a file
LAST_SYNC_FILE = "last_sync.txt"

def get_last_sync_date():
    try:
        with open(LAST_SYNC_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    except FileNotFoundError:
        # If no previous sync, start from epoch
        return datetime(1970, 1, 1)

def update_last_sync_date(date):
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(date.isoformat())

def delta_sync(raw_products):
    """
    Return only products updated since last sync.
    """
    last_sync = get_last_sync_date()
    updated_products = [
        p for p in raw_products
        if datetime.fromisoformat(p.get("updated_at")) > last_sync
    ]
    
    if updated_products:
        # Update last sync timestamp to the newest updated_at
        newest = max(datetime.fromisoformat(p["updated_at"]) for p in updated_products)
        update_last_sync_date(newest)
    
    return updated_products

# Example usage
raw_products = [
    {"sku": "A1", "updated_at": "2025-11-10T12:00:00"},
    {"sku": "B2", "updated_at": "2025-11-12T09:30:00"},
]

new_products = delta_sync(raw_products)
print(new_products)

