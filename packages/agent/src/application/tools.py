from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from typing import Any, Dict, List

from src.adapters.pluggy_provider import pluggy_provider
from src.dependencies import accounts_repository, transactions_repository

@tool
def create_connect_token(config: RunnableConfig) -> Dict[str, Any]:
    """
    Creates a connection token for the current user.
    Use this when you need to let the user connect their bank account.
    Returns a dictionary containing the access token.
    """
    client_user_id = config.get("configurable", {}).get("client_user_id")
    if not client_user_id:
        return {"error": "Missing client_user_id in runtime configuration."}
        
    return pluggy_provider.create_connect_token(client_user_id)

@tool
def get_user_accounts(config: RunnableConfig) -> List[Dict[str, Any]]:
    """
    Fetches the list of bank accounts after the user has successfully connected their bank.
    Returns a list of connected accounts.
    """
    item_id = config.get("configurable", {}).get("item_id")
    if not item_id:
        return [{"error": "Missing item_id in runtime configuration. The user may not have finished connecting their bank."}]
        
    db_accounts = accounts_repository.get_accounts_by_item(item_id)
    return [acc.dict() for acc in db_accounts]

@tool
def get_account_transactions(account_id: str) -> List[Dict[str, Any]]:
    """
    Fetches a list of transactions for a specific bank account.
    Requires the specific `account_id`.
    Returns a list of transactions.
    """
    db_transactions = transactions_repository.get_transactions_by_account(account_id)
    return [t.dict() for t in db_transactions]
