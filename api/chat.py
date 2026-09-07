from contextlib import asynccontextmanager
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from graph.workflow import graph
from mcp_tools.mcp_client import init_mcp, close_mcp

from utils.logger import logger
from utils.db import create_table, get_chat_history, save_chat
from utils.query_rewriter import rewrite_query


# ============================================================
# Application Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_DIR = BASE_DIR / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_DB = MEMORY_DIR / "langgraph_checkpoints.db"


# ============================================================
# LangGraph + MCP Application Lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting HealthCare AI Application...")

    try:
        # ----------------------------------------------------
        # Initialize MCP once for the application lifetime.
        # ----------------------------------------------------
        logger.info("Initializing MCP client...")
        await init_mcp()

        # ----------------------------------------------------
        # Create LangGraph checkpointer.
        # ----------------------------------------------------
        logger.info("Starting LangGraph checkpointer...")

        async with AsyncSqliteSaver.from_conn_string(
            str(CHECKPOINT_DB)
        ) as checkpointer:

            # ------------------------------------------------
            # Compile the graph only once at startup. #explanations-4
            # ------------------------------------------------
            app.state.workflow = graph.compile(
                checkpointer=checkpointer
            )

            logger.info(
                "LangGraph compiled successfully..."
            )

            # ------------------------------------------------
            # Application is running here.
            # ------------------------------------------------
            yield #explanations-5

    finally: #explanations-5

        # ----------------------------------------------------
        # Close MCP when FastAPI shuts down.
        # ----------------------------------------------------
        logger.info("Closing MCP client...")

        try:
            await close_mcp()
        except Exception as exc:
            logger.error(
                f"Error while closing MCP client: {exc}"
            )

        logger.info(
            "HealthCare Application API shutdown completed."
        )


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Agentika AI — Agentic Intelligence Platform",
    description=(
        "MCP-powered Agentic AI platform using "
        "LangGraph, RAG, local LLMs, tool orchestration, "
        "human review, validation, and appointment workflows."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Database Initialization
# ============================================================

try:

    create_table()

    logger.info(
        "Chat history database initialized successfully..."
    )

except Exception as exc:

    logger.error(
        f"Error while initializing chat history database: {exc}"
    )


# ============================================================
# Request / Response Schemas
# ============================================================

class ChatRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="User's natural-language query."
    )

    session_id: str | None = Field(
        default=None,
        description=(
            "Conversation/session ID. "
            "Reuse the same ID for follow-up questions."
        )
    )

    user_role: str = Field(
        default="patient",
        description="Role of the user interacting with the system."
    )


class ChatResponse(BaseModel):

    answer: str

    session_id: str


# ============================================================
# Health Check
# ============================================================

@app.get("/")
async def health_check():

    return {
        "status": "healthy",
        "service": "Agentika AI",
    }


# ============================================================
# Chat Endpoint
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(req: ChatRequest):

    # --------------------------------------------------------
    # Session Management
    # --------------------------------------------------------

    session_id = (
        req.session_id
        or str(uuid.uuid4())
    )

    logger.info(
        f"Incoming chat request | session={session_id}"
    )

    try:

        # ----------------------------------------------------
        # Load previous conversation history.
        #
        # This is important for query rewriting and
        # multi-turn conversations.
        # ----------------------------------------------------

        chat_history = get_chat_history(
            session_id
        )

        logger.info(
            f"Conversation history loaded | session={session_id}"
        )


        # ----------------------------------------------------
        # Query Rewriting
        #
        # Example:
        #
        # User:
        #   What is the refund policy?
        #
        # Follow-up:
        #   What about that?
        #
        # Query rewriter:
        #   What is the company's refund policy?
        #
        # The rewritten query is then passed into LangGraph.
        # ----------------------------------------------------

        rewritten_query = await rewrite_query(
            req.query,
            chat_history
        )

        logger.info(
            f"Query rewritten | session={session_id}"
        )

        logger.info(
            f"Rewritten query: {rewritten_query}"
        )


        # --------------------------------------------------------
    # 4. Redis Cache Lookup
    # --------------------------------------------------------

        cache_key = (
        f"llm:{rewritten_query.lower().strip()}"
        )

        cached = get_cache(cache_key)

        if cached:

           logger.info(
            "Redis cache hit"
            )

           return {
            "answer": cached,
            "session_id": session_id
            }
            
        logger.info(
                "Redis cache miss"
            )


        # ----------------------------------------------------
        # Initial LangGraph State
        # ----------------------------------------------------

        initial_state = {

            # User / session
            "user_query": req.query,
            "user_role": req.user_role,
            "conversation_history": chat_history,

            # Rewritten query
            "rewritten_query": rewritten_query,

            # Orchestration
            "request_type": "",
            "route": "",
            "risk_level": "",

            # Appointment
            "appointment_doctor": "",
            "appointment_specialization": "",
            "appointment_date": "",
            "appointment_time": "",
            "appointment_result": "",

            # RAG
            "context": "",
            "sources": [],
            "retrieval_status": "",

            # MCP tools
            "tool_result": "",

            # Response
            "draft_answer": "",

            # Human review
            "review_status": "",
            "reviewer_feedback": "",
            "modified_answer": "",

            # Validation
            "validation_status": "",
            "validation_reason": "",

            # Final answer
            "final_answer": "",

            # Retry
            "retry_count": 0,
        }


        # ----------------------------------------------------
        # LangGraph Thread Configuration
        #
        # Same session_id = same LangGraph conversation thread.
        # ----------------------------------------------------

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }


        # ----------------------------------------------------
        # Execute LangGraph
        # ----------------------------------------------------

        logger.info(
            f"Invoking LangGraph | session={session_id}"
        )

        result = await app.state.workflow.ainvoke(
            initial_state,
            config=config
        )


        # ----------------------------------------------------
        # Get final answer produced by the graph.
        #
        # IMPORTANT:
        # Do NOT call the LLM again here.
        #
        # response_node -> draft_answer
        # validator_node -> final_answer
        # appointment_node -> final_answer
        # rejection_node -> final_answer
        # retry_exhausted_node -> final_answer
        # ----------------------------------------------------

        answer = result.get(
            "final_answer",
            ""
        )


        # ----------------------------------------------------
        # Safety fallback
        # ----------------------------------------------------

        if not answer:

            logger.error(
                f"LangGraph returned no final answer "
                f"| session={session_id}"
            )

            raise HTTPException(
                status_code=500,
                detail="Workflow completed without a final answer."
            )


        # ----------------------------------------------------
        # Save Conversation History
        # ----------------------------------------------------

        logger.info(
            f"Saving chat history | session={session_id}"
        )

        save_chat(
            session_id,
            req.query,
            answer
        )


        # ----------------------------------------------------
        # Log Workflow Result
        # ----------------------------------------------------

        logger.info(
            f"Workflow completed | "
            f"session={session_id} | "
            f"route={result.get('route')} | "
            f"risk={result.get('risk_level')} | "
            f"validation={result.get('validation_status')}"
        )


        # ----------------------------------------------------
        # Return API Response
        # ----------------------------------------------------

        return ChatResponse(
            answer=answer,
            session_id=session_id
        )


    except HTTPException:
        raise


    except Exception as exc:

        logger.exception(
            f"Chat request failed | "
            f"session={session_id} | "
            f"error={exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the request."
        )