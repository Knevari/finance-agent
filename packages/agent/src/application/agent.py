import os
from dotenv import load_dotenv

load_dotenv()
from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from src.application.tools import create_connect_token, get_user_accounts, get_account_transactions

# Load the system prompt
prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.md')
with open(prompt_path, 'r', encoding='utf-8') as f:
    system_prompt_text = f.read()

model = init_chat_model(model="google_genai:gemini-2.5-flash-lite", api_key=os.environ['GOOGLE_API_KEY'])

# Initialize Tavily search tool
search = TavilySearchResults(max_results=3)

# Initialize Checkpointer
conn = sqlite3.connect("finance_agent_memory.db", check_same_thread=False)
memory = SqliteSaver(conn)

agent = create_react_agent(
    model, 
    tools=[search, create_connect_token, get_user_accounts, get_account_transactions],
    prompt=system_prompt_text,
    checkpointer=memory
)