import os
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()


class MagentoClient:
    """Reusable Magento API client for OAuth1 connections."""

    def __init__(self):
        self.base_url = os.getenv("MAGENTO_BASE_URL")
        self.consumer_key = os.getenv("MAGENTO_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MAGENTO_CONSUMER_SECRET")
        self.access_token = os.getenv("MAGENTO_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("MAGENTO_ACCESS_TOKEN_SECRET")

        if not all([
            self.base_url,
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret,
        ]):
            raise ValueError("❌ Missing Magento credentials in .env")

        self.auth = OAuth1(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret,
            signature_method="HMAC-SHA256"
        )

    def get(self, endpoint, params=None):
        """Perform GET request."""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, auth=self.auth, params=params, timeout=20)
        if response.status_code != 200:
            raise Exception(
                f"Magento GET failed [{response.status_code}] → {response.text}"
            )
        return response.json()

    def post(self, endpoint, payload):
        """Perform POST request."""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, auth=self.auth, json=payload, timeout=20)
        if response.status_code not in (200, 201):
            raise Exception(
                f"Magento POST failed [{response.status_code}] → {response.text}"
            )
        return response.json()
