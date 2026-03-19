import sys
import os
from pathlib import Path

# Add the agent package to the Python path
agent_dir = Path(__file__).parent.parent / 'agent'
sys.path.insert(0, str(agent_dir.resolve()))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests

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
    try:
        return pluggy_provider.create_connect_token(request.client_user_id)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        try:
            detail = e.response.json().get("message", str(e))
        except:
            detail = str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pluggy/sync")
def sync_pluggy_data(request: SyncRequest):
    """
    Saves the user's item_id to the database and syncs their accounts 
    and transactions locally to prevent rate limiting.
    """
    try:
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
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        try:
            detail = e.response.json().get("message", str(e))
        except:
            detail = str(e)
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
    def event_generator():
        print(f"Chat stream started for user: {request.client_user_id}")
        # Use stream_mode="messages" for standard chat streaming
        try:
            for msg, metadata in agent.stream(
                {"messages": [("user", request.message)]}, 
                config=config,
                stream_mode="messages"
            ):
                # Standardize message to a dict for sending
                try:
                    # LangChain messages have a dict() method or we can use .json()
                    # But for streaming we want to be lightweight.
                    msg_dict = {
                        "type": getattr(msg, 'type', 'unknown'),
                        "content": msg.content,
                        "id": getattr(msg, 'id', None),
                    }
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        msg_dict["tool_calls"] = msg.tool_calls
                        
                    yield f"data: {json.dumps({'messages': [msg_dict]})}\n\n"
                except Exception as inner_e:
                    print(f"Error serializing message: {inner_e}")
                        
        except Exception as e:
            print(f"Chat stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        print("Chat stream finished")
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "ok"}
