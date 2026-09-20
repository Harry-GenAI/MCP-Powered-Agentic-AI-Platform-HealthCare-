from contextlib import asynccontextmanager
from pathlib import Path
import uuid
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from graph.workflow import graph

from mcp_tools.mcp_client import (
    init_mcp,
    close_mcp,
)

from utils.logger import logger

from database.db import (
    create_table,
    get_chat_history,
    save_chat,
)

from utils.query_rewriter import rewrite_query

from middleware.cache import set_cache


# ============================================================
# Application Paths
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

MEMORY_DIR = (
    BASE_DIR / "memory"
)

MEMORY_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CHECKPOINT_DB = (
    MEMORY_DIR /
    "langgraph_checkpoints.db"
)


# ============================================================
# LangGraph + MCP Lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    logger.info(
        "Starting HealthCare AI Application..."
    )

    try:

        logger.info(
            "Initializing MCP client..."
        )

        await init_mcp()

        logger.info(
            "Starting LangGraph checkpointer..."
        )

        async with AsyncSqliteSaver.from_conn_string(
            str(CHECKPOINT_DB)
        ) as checkpointer:

            app.state.workflow = graph.compile(
                checkpointer=checkpointer
            )

            logger.info(
                "LangGraph compiled successfully..."
            )

            yield #explanations-5

    finally: #explanations-5

        logger.info(
            "Closing MCP client..."
        )

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
# Request Schemas
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
        description=(
            "Role of the user interacting with the system."
        )
    )


class ReviewRequest(BaseModel):

    session_id: str = Field(
        ...,
        description=(
            "Session ID of the paused human-review workflow."
        )
    )

    decision: Literal[
        "approve",
        "modify",
        "reject"
    ]

    reviewer_feedback: str = Field(
        default="",
        description=(
            "Optional feedback from the authorized reviewer."
        )
    )

    final_answer: str = Field(
        default="",
        description=(
            "Final answer written by the authorized "
            "reviewer for approve/modify decisions."
        )
    )


# ============================================================
# Response Schema
# ============================================================

class ChatResponse(BaseModel):

    answer: str = ""

    session_id: str

    status: Literal[
        "completed",
        "review_required"
    ] = "completed"

    review_required: bool = False

    review_request: dict | None = None

    sources: list = []

    route: str = ""

    risk_level: str = ""


# ============================================================
# Interrupt Helper
# ============================================================

def get_interrupt_payload(
    result: dict
):

    interrupts = result.get(
        "__interrupt__"
    )

    if not interrupts:
        return None

    interrupt_obj = interrupts[0]

    if hasattr(
        interrupt_obj,
        "value"
    ):
        return interrupt_obj.value

    if isinstance(
        interrupt_obj,
        dict
    ):
        return interrupt_obj

    return {
        "message": str(
            interrupt_obj
        )
    }


# ============================================================
# Pending Review Response
# ============================================================

def build_pending_response(
    session_id: str,
    result: dict
) -> ChatResponse:

    return ChatResponse(

        answer=(
            "This request requires review by an "
            "authorized healthcare reviewer before "
            "a final response can be provided."
        ),

        session_id=session_id,

        status="review_required",

        review_required=True,

        review_request=get_interrupt_payload(
            result
        ),

        sources=result.get(
            "sources",
            []
        ),

        route=result.get(
            "route",
            ""
        ),

        risk_level=result.get(
            "risk_level",
            ""
        ),
    )


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
async def chat(
    req: ChatRequest
):

    session_id = (
        req.session_id
        or str(uuid.uuid4())
    )

    logger.info(
        f"Incoming chat request | session={session_id}"
    )

    try:

        # ----------------------------------------------------
        # Conversation History
        # ----------------------------------------------------

        chat_history = get_chat_history(
            session_id
        )

        logger.info(
            f"Conversation history loaded | "
            f"session={session_id}"
        )

        # ----------------------------------------------------
        # Query Rewriting
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

        # ----------------------------------------------------
        # Initial LangGraph State
        # ----------------------------------------------------

        initial_state = {

            # User / Session
            "user_query": req.query,
            "user_role": req.user_role,
            "conversation_history": chat_history,

            # Query rewriting
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

            # MCP
            "tool_result": "",

            # Response
            "draft_answer": "",

            # Human Review
            # IMPORTANT:
            # These must start EMPTY.
            # The reviewer response comes later
            # through Command(resume=...).
            "review_status": "",
            "reviewer_feedback": "",
            "modified_answer": "",

            # Validation
            "validation_status": "",
            "validation_reason": "",

            # Final
            "final_answer": "",

            # Retry
            "retry_count": 0,
        }

        # ----------------------------------------------------
        # LangGraph Thread
        # ----------------------------------------------------

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        logger.info(
            f"Invoking LangGraph | session={session_id}"
        )

        # ----------------------------------------------------
        # Execute Graph
        # ----------------------------------------------------

        result = await app.state.workflow.ainvoke(
            initial_state,
            config=config
        )

        # ----------------------------------------------------
        # HUMAN-IN-THE-LOOP INTERRUPT
        # ----------------------------------------------------

        if result.get("__interrupt__"): #explanations - 8

            logger.info(
                f"Human review required | "
                f"session={session_id}"
            )

            return build_pending_response(
                session_id,
                result
            )

        # ----------------------------------------------------
        # Completed Workflow
        # ----------------------------------------------------

        answer = result.get(
            "final_answer",
            ""
        )

        if not answer:

            logger.error(
                f"LangGraph returned no final answer "
                f"| session={session_id}"
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Workflow completed without "
                    "a final answer."
                )
            )

        # ----------------------------------------------------
        # Save Chat
        # ----------------------------------------------------

        save_chat(
            session_id,
            req.query,
            answer
        )

        # ----------------------------------------------------
        # Redis Cache
        #
        # Only cache completed, low-risk,
        # informational RAG responses.
        # ----------------------------------------------------

        if (
            result.get("risk_level") == "low"
            and result.get("route")
            in {
                "internal_rag",
                "vendor_rag",
            }
        ):

            cache_key = (
                f"llm:"
                f"{rewritten_query.lower().strip()}"
            )

            try:

                set_cache(
                    cache_key,
                    answer
                )

                logger.info(
                    "Safe response stored in Redis cache"
                )

            except Exception as exc:

                logger.exception(
                    f"Redis cache write failed: {exc}"
                )

        # ----------------------------------------------------
        # Workflow Log
        # ----------------------------------------------------

        logger.info(
            f"Workflow completed | "
            f"session={session_id} | "
            f"route={result.get('route')} | "
            f"risk={result.get('risk_level')} | "
            f"validation={result.get('validation_status')}"
        )

        # ----------------------------------------------------
        # Return
        # ----------------------------------------------------

        return ChatResponse(

            answer=answer,

            session_id=session_id,

            status="completed",

            review_required=False,

            sources=result.get(
                "sources",
                []
            ),

            route=result.get(
                "route",
                ""
            ),

            risk_level=result.get(
                "risk_level",
                ""
            ),
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
            detail=(
                "An error occurred while "
                "processing the request."
            )
        )


# ============================================================
# HUMAN REVIEW RESUME ENDPOINT
# ============================================================

@app.post(
    "/review",
    response_model=ChatResponse
)
async def submit_review(
    req: ReviewRequest
):

    session_id = req.session_id

    logger.info(
        f"Human review submitted | "
        f"session={session_id} | "
        f"decision={req.decision}"
    )

    # --------------------------------------------------------
    # Approve / Modify requires a final human-written answer.
    # --------------------------------------------------------

    if (
        req.decision in {
            "approve",
            "modify",
        }
        and not req.final_answer.strip()
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "final_answer is required when the "
                "reviewer approves or modifies the request."
            )
        )

    # --------------------------------------------------------
    # Resume Payload
    # --------------------------------------------------------

    resume_value = {

        "decision": req.decision,

        "reviewer_feedback":
            req.reviewer_feedback,

        "final_answer":
            req.final_answer,
    }

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    try:

        # ----------------------------------------------------
        # Resume interrupted LangGraph workflow
        # ----------------------------------------------------

        result = await app.state.workflow.ainvoke(

            Command(
                resume=resume_value
            ),

            config=config
        )

        # ----------------------------------------------------
        # Defensive interrupt check
        # ----------------------------------------------------

        if result.get(
            "__interrupt__"
        ):

            logger.error(
                f"Workflow requested another review | "
                f"session={session_id}"
            )

            return build_pending_response(
                session_id,
                result
            )

        # ----------------------------------------------------
        # Final Human-Approved / Modified Answer
        # ----------------------------------------------------

        answer = result.get(
            "final_answer",
            ""
        )

        if not answer:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Review completed without "
                    "a final answer."
                )
            )

        # ----------------------------------------------------
        # Save Reviewed Conversation
        # ----------------------------------------------------

        save_chat(
            session_id,
            result.get(
                "user_query",
                "[Human-reviewed request]"
            ),
            answer
        )

        logger.info(
            f"Human review workflow completed | "
            f"session={session_id} | "
            f"status={result.get('review_status')}"
        )

        # ----------------------------------------------------
        # Return
        # ----------------------------------------------------

        return ChatResponse(

            answer=answer,

            session_id=session_id,

            status="completed",

            review_required=False,

            sources=result.get(
                "sources",
                []
            ),

            route=result.get(
                "route",
                ""
            ),

            risk_level=result.get(
                "risk_level",
                ""
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            f"Human review failed | "
            f"session={session_id} | "
            f"error={exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred while "
                "resuming the review workflow."
            )
        )