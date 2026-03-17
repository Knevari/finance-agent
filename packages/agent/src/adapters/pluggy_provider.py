import os
from pluggy_sdk import PluggyClient
from typing import Any, Dict, List

from src.ports.financial_data_provider import FinancialDataProvider

class PluggyProvider(FinancialDataProvider):
    """
    Pluggy implementation of the FinancialDataProvider.
    Handles the Pluggy lifecycle and API interactions.
    """
    def __init__(self):
        self.client = PluggyClient(
            client_id=os.environ['PLUGGY_CLIENT_ID'],
            client_secret=os.environ['PLUGGY_CLIENT_SECRET']
        )

    def create_connect_token(self, client_user_id: str) -> Dict[str, Any]:
        connect_token = self.client.create_connect_token(
            client_user_id=client_user_id
        )
        return {'accessToken': connect_token.access_token}

    def get_accounts(self, item_id: str) -> List[Dict[str, Any]]:
        # Using the pluggy_sdk to fetch accounts for a given item_id.
        # Note: Depending on the SDK structure, this might require specific pagination handling
        # For simplicity, we assume fetch_accounts returns a paginated response object.
        accounts_response = self.client.fetch_accounts(item_id=item_id)
        # Convert to a list of dicts for the generic interface
        return [account.dict() for account in accounts_response.results]

    def get_transactions(self, account_id: str) -> List[Dict[str, Any]]:
        # Using the pluggy_sdk to fetch transactions for a given account_id.
        transactions_response = self.client.fetch_transactions(account_id=account_id)
        # Convert to a list of dicts for the generic interface
        return [transaction.dict() for transaction in transactions_response.results]

# Instantiate a default provider for easy importing
pluggy_provider = PluggyProvider()