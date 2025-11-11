from src.utils.magento_client import MagentoClient
import json, time, os

client = MagentoClient()

def fetch_all_products(page_size=100):
    all_items = []
    page = 1

    while True:
        print(f"📦 Fetching page {page} ...")
        params = {
            "searchCriteria[currentPage]": page,
            "searchCriteria[pageSize]": page_size,
        }
        data = client.get("/V1/products", params=params)
        items = data.get("items", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < page_size:
            break
        page += 1
        time.sleep(1)
    return all_items

if __name__ == "__main__":
    products = fetch_all_products()
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/magento_products_full.json", "w") as f:
        json.dump(products, f, indent=2)
    print(f"✅ Saved {len(products)} products to file.")
