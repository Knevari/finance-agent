from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class AccountInfo(BaseModel):
    id: str
    item_id: str
    name: str = ""
    type: str = ""
    balance: float = 0.0

class TransactionInfo(BaseModel):
    id: str
    account_id: str
    amount: float = 0.0
    date: str = ""
    description: str = ""

class UserInfo(BaseModel):
    client_user_id: str
    pluggy_item_id: Optional[str] = None
