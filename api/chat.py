from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from langgraph_workflow import graph

from utils.logger import logger
from utils.db import create_table, get_chat_history, save_chat
from utils.query_rewriter import rewrite_query

from middleware.cache import get_cache, set_cache

from prompts.prompts import build_prompt
from llm.llm_service import generate_reply



# ============================================================
# LangGraph Lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting LangGraph checkpointer...")

    # Create and maintain the LangGraph checkpointer
    # for the lifetime of the FastAPI application.
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:

        # Compile the graph only once during application startup.
        app.state.workflow = graph.compile(
            checkpointer=memory
        )

        logger.info("LangGraph compiled successfully...")

        # Application runs while execution is paused here.
        yield

    # Executed when FastAPI shuts down.
    logger.info("LangGraph checkpointer closed...")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="MCP-Powered Agentic Orchestration System (MAOS)",
    lifespan=lifespan
)


# ============================================================
# Database Initialization
# ============================================================

try:
    create_table()
    logger.info("Database table initialized successfully...")

except Exception as e:
    logger.error(f"Error while creating database table: {e}")


# ============================================================
# Request / Response Schemas
# ============================================================

class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None
    domain: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


# ============================================================
# Health Check
# ============================================================

@app.get("/")
def health_check():

    logger.info("Health check called")

    return {
        "status": "healthy"
    }


# ============================================================
# Main Chat Endpoint
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):

    # --------------------------------------------------------
    # Session Management
    # --------------------------------------------------------

    session_id = req.session_id or str(uuid.uuid4())

    # Retrieve previous conversation history.
    chat_history = get_chat_history(session_id)

    # --------------------------------------------------------
    # Query Rewriting
    # --------------------------------------------------------

    # Rewrite the user's query using conversation history
    # so retrieval and routing receive a better query.
    rewritten_query = await rewrite_query(
        req.query,
        chat_history
    )

    # --------------------------------------------------------
    # Redis Cache Lookup
    # --------------------------------------------------------

    cache_key = f"llm:{rewritten_query.lower().strip()}"

    cached = get_cache(cache_key)

    if cached:

        logger.info("Redis cache hit")

        return {
            "answer": cached,
            "session_id": session_id
        }

    logger.info("Redis cache miss")

    # --------------------------------------------------------
    # Initial LangGraph State
    # --------------------------------------------------------

    initial_state = {
        "user_query": req.query,
        "rewritten_query": rewritten_query,
        "route": "",
        "response": "",
        "approval": ""
    }

    # LangGraph uses the session ID as the thread ID
    # for checkpointed conversation state.
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # --------------------------------------------------------
    # Execute LangGraph Workflow
    # --------------------------------------------------------

    result = await app.state.workflow.ainvoke(
        initial_state,
        config=config
    )

    context = result["response"]

    # --------------------------------------------------------
    # Build Final LLM Prompt
    # --------------------------------------------------------

    prompt = build_prompt(
        context,
        rewritten_query
    )

    # --------------------------------------------------------
    # Generate Final LLM Response
    # --------------------------------------------------------

    answer = await generate_reply(prompt)

    # --------------------------------------------------------
    # Save Conversation History
    # --------------------------------------------------------

    logger.info(f"Saving chat for session: {session_id}")

    save_chat(
        session_id,
        req.query,
        answer
    )

    # --------------------------------------------------------
    # Store Final Answer in Redis
    # --------------------------------------------------------

    logger.info("Saving response to Redis cache")

    set_cache(
        cache_key,
        answer
    )

    # --------------------------------------------------------
    # Return API Response
    # --------------------------------------------------------

    return {
        "answer": answer,
        "session_id": session_id
    }