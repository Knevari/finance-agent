import sys
import os
from pathlib import Path

# Add the agent package to the Python path
agent_dir = Path(__file__).parent.parent.parent / 'agent'
sys.path.append(str(agent_dir.resolve()))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from src.application.agent import agent
from src.adapters.pluggy_provider import pluggy_provider
from src.adapters.sqlalchemy_repository import db_adapter
from src.domain.models import AccountInfo, TransactionInfo

app = FastAPI(title="Finance Agent API")

# Add CORS so the Next.js frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    client_user_id: str | None = None
    thread_id: str | None = None

class SyncRequest(BaseModel):
    client_user_id: str
    item_id: str

class TokenRequest(BaseModel):
    client_user_id: str

@app.post("/pluggy/token")
def create_token(request: TokenRequest):
    return pluggy_provider.create_connect_token(request.client_user_id)

@app.post("/pluggy/sync")
def sync_pluggy_data(request: SyncRequest):
    """
    Saves the user's item_id to the database and syncs their accounts 
    and transactions locally to prevent rate limiting.
    """
    # 1. Save user and item_id
    db_adapter.save_user_item(request.client_user_id, request.item_id)
    
    # 2. Fetch accounts from Pluggy
    pluggy_accounts = pluggy_provider.get_accounts(request.item_id)
    domain_accounts = []
    
    for pa in pluggy_accounts:
        acc = AccountInfo(
            id=pa.get('id'), 
            item_id=request.item_id, 
            name=pa.get('name', 'Unknown'), 
            type=pa.get('type', 'Unknown'), 
            balance=float(pa.get('balance', 0.0))
        )
        domain_accounts.append(acc)
        
        # 3. Fetch transactions for each account from Pluggy
        pluggy_transactions = pluggy_provider.get_transactions(acc.id)
        domain_transactions = []
        for pt in pluggy_transactions:
            dt = TransactionInfo(
                id=pt.get('id'),
                account_id=acc.id,
                amount=float(pt.get('amount', 0.0)),
                date=str(pt.get('date', '')),
                description=pt.get('description', '')
            )
            domain_transactions.append(dt)
        db_adapter.save_transactions(domain_transactions)

    db_adapter.save_accounts(domain_accounts)
    return {"status": "success"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to interact with the finance agent.
    Streams back the response chunks.
    """
    # Look up the user's item_id from the database
    item_id = None
    if request.client_user_id:
        user_info = db_adapter.get_user_by_client_id(request.client_user_id)
        if user_info:
            item_id = user_info.pluggy_item_id

    config = {
        "configurable": {
            "client_user_id": request.client_user_id,
            "item_id": item_id,
            "thread_id": request.thread_id or "default_thread_1"
        }
    }
    
    async def event_generator():
        # Agent stream yields chunks of execution.
        # We catch format issues by providing a default stringifier.
        try:
            for chunk in agent.stream(
                {"messages": [("user", request.message)]}, 
                config=config
            ):
                yield f"data: {json.dumps(chunk, default=str)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "ok"}
