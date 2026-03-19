# Finance Agent

An intelligent, conversational banking and finance advisor built with LangChain, FastAPI, Next.js, and the Pluggy API. 

This project utilizes a scalable Monorepo design, Hexagonal Architecture for its integrations, and LangGraph checkpointers for persistent conversational memory.

## Architecture & Monorepo Structure

The project is structured entirely inside the `packages/` directory, allowing frontends and backends to scale independently while keeping the repository unified.

```
finance-agent/
├── packages/
│   ├── agent/        # Core LLM Engine (Hexagonal Architecture)
│   ├── agent-api/    # FastAPI wrapper exposing the Agent & maintaining sync logic
│   └── frontend/     # Next.js React UI displaying the chat and Pluggy widget
├── Taskfile.yml      # Orchestration commands
├── .env              # Environment variables
└── README.md
```

### 1. The Core Agent (`packages/agent`)
Built with LangGraph (`create_react_agent`), the agent acts as your financial planner. It uses the `google-genai:gemini-2.5-flash` model and features Tavily web search.
The package strictly follows **Hexagonal Architecture**:
- **`src/domain/`**: Abstract data models for Users, Accounts, and Transactions.
- **`src/ports/`**: Interfaces such as `DatabaseRepository` and `FinancialDataProvider`.
- **`src/adapters/`**: Concrete implementations of the ports. Features a scalable `SQLAlchemyAdapter` (for easy SQLite -> Postgres migrations) and a `PluggyProvider`.
- **`src/application/`**: Contains the tools (`tools.py`) and the LangGraph graph creation (`agent.py`). It uses `SqliteSaver` to persist LLM memory across requests based on `thread_id`.

### 2. The API Backend (`packages/agent-api`)
A FastAPI server that wraps the inner Agent module, providing security boundaries and streaming capabilities.
- **`/chat`**: Securely looks up the user's `item_id` and invokes the agent, streaming Server-Sent Events (SSE) back to the UI.
- **`/pluggy/token`**: Generates connection tokens without exposing the Pluggy Secret to the browser.
- **`/pluggy/sync`**: To prevent rate limiting from the bank provider, this endpoint syncs financial states from Pluggy into the local SQLAlchemy SQLite Database (`finance_agent.db`). All agent queries are made against this local cache!

### 3. The Frontend (`packages/frontend`)
A sleek Next.js chat interface adapted from `langgraph-sdk/react-ui`.
- Integrates the `<PluggyConnectWidget />` allowing users to securely link their bank directly from the chat header.
- Subscribes to the backend `/chat` stream to display LLM reasoning and tools in real-time.

---

## Getting Started

### Prerequisites
You need the following API Keys in your `.env` file at the root of the project:
```env
PLUGGY_CLIENT_ID="your_pluggy_id"
PLUGGY_CLIENT_SECRET="your_pluggy_secret"
GOOGLE_API_KEY="your_gemini_api_key"
TAVILY_API_KEY="your_tavily_api_key"
```

### Running the Application

This project uses `uv` for python dependency management and `Taskfile` to simplify concurrent startup commands.
Make sure you have [uv](https://github.com/astral-sh/uv) and [Task](https://taskfile.dev/) installed.

**Setup Backend Environment:**
```bash
uv venv
uv pip install -r requirements.txt
```

**Running everything together:**
```bash
task dev
```

**Running individually:**
```bash
task api       # Runs Uvicorn for FastAPI on port 8000
task frontend  # Runs Next.js dev server on port 3000
```
