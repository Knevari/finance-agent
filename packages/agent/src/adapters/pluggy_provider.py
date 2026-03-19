import os
import requests

from dotenv import load_dotenv
from typing import Any, Dict, List

from src.ports.financial_data_provider import FinancialDataProvider

class PluggyProvider(FinancialDataProvider):
    """
    HTTP implementation of the FinancialDataProvider targeting Pluggy's REST API.
    """
    def __init__(self):
        load_dotenv()
        self.client_id = os.environ.get('PLUGGY_CLIENT_ID')
        self.client_secret = os.environ.get('PLUGGY_CLIENT_SECRET')
        self.base_url = "https://api.pluggy.ai"
        self._api_key = None

    def _get_api_key(self) -> str:
        if self._api_key:
            return self._api_key
            
        res = requests.post(f"{self.base_url}/auth", json={
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        })
        res.raise_for_status()
        self._api_key = res.json().get("apiKey")
        return self._api_key

    def _headers(self) -> dict:
        return {
            "X-API-KEY": self._get_api_key(),
            "Content-Type": "application/json"
        }

    def create_connect_token(self, client_user_id: str) -> Dict[str, Any]:
        res = requests.post(f"{self.base_url}/connect_token", headers=self._headers(), json={
            "clientUserId": client_user_id
        })
        res.raise_for_status()
        return {'accessToken': res.json().get("accessToken")}

    def get_accounts(self, item_id: str) -> List[Dict[str, Any]]:
        res = requests.get(f"{self.base_url}/accounts", headers=self._headers(), params={
            "itemId": item_id
        })
        res.raise_for_status()
        return res.json().get("results", [])

    def get_transactions(self, account_id: str) -> List[Dict[str, Any]]:
        res = requests.get(f"{self.base_url}/transactions", headers=self._headers(), params={
            "accountId": account_id
        })
        res.raise_for_status()
        return res.json().get("results", [])

# Instantiate a default provider for easy importing
pluggy_provider = PluggyProvider()