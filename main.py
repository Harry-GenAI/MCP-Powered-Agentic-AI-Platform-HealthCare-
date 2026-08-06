from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import asyncio
import os
import time

from utils.logger import logger
from utils.db import create_table, save_chat, get_chat_history
from prometheus_fastapi_instrumentator import Instrumentator


# -----------------------------------------------------
# Ensure vector index exists (auto-ingest for container)
# -----------------------------------------------------
if not os.path.exists("chroma_db") or not os.listdir("chroma_db"):
    logger.info("Chroma index missing; running ingestion pipeline")

    from ingest.ingest import main as ingest_main
    ingest_main()

from rag.rag import retrieve_context
from llm.llmservice_vllm import generate_reply
from prompts.prompts import build_prompt
from safety.safety import is_safe_input
from utils.query_rewriter import rewrite_query


# ---------------------------------------------------------
# APP INITIALIZATION
# ---------------------------------------------------------
logger.info("Starting Enterprise RAG API")

try:
    create_table()
except Exception:
    logger.exception("Chat history table initialization failed; continuing without memory")

app = FastAPI()

Instrumentator().instrument(app).expose(app)  # for prometheus


# ---------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    domain: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[str]
    context: str


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@app.get("/")
def health():
    logger.info("Health check called")
    return {"status": "PLRS is Running.."}


# ---------------------------------------------------------
# MAIN CHAT ENDPOINT
# ---------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):

    api_start = time.time()

    # create or reuse session
    session_id = req.session_id or str(uuid.uuid4())

    logger.info(f"New chat request | session={session_id}")

    # -----------------------------------------------------
    # Guardrails check
    # -----------------------------------------------------
    if not is_safe_input(req.message):
        return {
            "answer": "Request blocked by policy.",
            "session_id": session_id,
            "sources": [],
            "context": ""
        }

    # -----------------------------------------------------
    # Load conversation memory
    # -----------------------------------------------------
    
    try:
        history = get_chat_history(session_id)
        logger.debug(f"[{session_id}] Memory took {time.time()-start:.3f} secs")
    except Exception:
        logger.exception("Chat history load failed; continuing without memory")
        history = ""

    # -----------------------------------------------------
    # Rewrite vague questions
    # -----------------------------------------------------
    start = time.time()
    if history:
        rewritten_query = await rewrite_query(req.message, history)
        logger.info(f"[{session_id}] Query Rewriting took {time.time()-start:.3f} secs")
    
    else:
        rewritten_query = req.message

    # -----------------------------------------------------
    # Metadata filter (domain routing)
    # -----------------------------------------------------
    metadata_filter = None

    if req.domain:
        metadata_filter = {
            "doc_type": req.domain
        }

    # -----------------------------------------------------
    # Retrieve context from vector store
    # -----------------------------------------------------
    rag_start = time.time()
    context, sources, retrieve_results = retrieve_context(
    rewritten_query,
    metadata_filter=metadata_filter,
    session_id=session_id
    )
    logger.info(f"{session_id} : RAGPP took {time.time()-rag_start:.3f} secs")   



    if not context:
        logger.warning("No retrieval context found")
        context = "No company knowledge found."

    # -----------------------------------------------------
    # Build final prompt
    # -----------------------------------------------------
    prompt = build_prompt(context, req.message)

    # -----------------------------------------------------
    # Call LLM
    # -----------------------------------------------------
    llm_start=time.time()
    answer = await generate_reply(prompt)
    logger.info(f"{session_id} : llm took {time.time()-llm_start:.3f} secs")
    
    # -----------------------------------------------------
    # Save conversation memory
    # -----------------------------------------------------
    
    save_chat(session_id, req.message, answer)

    logger.info(f"Response completed | session={session_id}")


    return {
        "answer": answer,
        "session_id": session_id,
        "sources": sources,
        "context": context
    }
