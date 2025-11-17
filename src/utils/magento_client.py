import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MagentoClient:
    """Magento client using Admin Token authentication."""

    def __init__(self):
        self.base_url = os.getenv("MAGENTO_BASE_URL")
        self.username = os.getenv("MAGENTO_ADMIN_USERNAME")
        self.password = os.getenv("MAGENTO_ADMIN_PASSWORD")

        if not all([self.base_url, self.username, self.password]):
            raise ValueError("❌ Missing Magento credentials in .env")

        self.token = self.get_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_token(self):
        """Request admin API token."""
        url = f"{self.base_url}/V1/integration/admin/token"
        res = requests.post(url, json={
            "username": self.username,
            "password": self.password
        })

        if res.status_code != 200:
            raise Exception(f"❌ Token request failed: {res.text}")

        return res.json()

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        res = requests.get(url, headers=self.headers, params=params, timeout=20)

        if res.status_code == 401:
            print("🔄 Token expired — refreshing...")
            self.token = self.get_token()
            self.headers["Authorization"] = f"Bearer {self.token}"
            res = requests.get(url, headers=self.headers, params=params, timeout=20)

        if res.status_code != 200:
            raise Exception(f"❌ Magento GET failed [{res.status_code}] → {res.text}")

        return res.json()
