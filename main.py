from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import asyncio
import os
import time

from logger import logger
from db import create_table, save_chat, get_chat_history
from prometheus_fastapi_instrumentator import Instrumentator


# -----------------------------------------------------
# Ensure vector index exists (auto-ingest for container)
# -----------------------------------------------------
if not os.path.exists("chroma_db") or not os.listdir("chroma_db"):
    logger.info("Chroma index missing; running ingestion pipeline")

    import ingest
    ingest.main()

from rag import retrieve_context
from llmservice_vllm import generate_reply
from prompts import build_prompt
from safety import is_safe_input
from query_rewriter import rewrite_query


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
    start = time.time()
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
        logger.debug(f"[{session_id}] Query Rewriting took {time.time()-start:.3f} secs")
    
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
    start = time.time()
    logger.debug(f"{session_id} Entering into RAG asyncio thread 💣")
    context, sources = retrieve_context(
    rewritten_query,
    metadata_filter=metadata_filter,
    session_id=session_id
)
    '''context, sources = await asyncio.to_thread(
        retrieve_context,
        rewritten_query,
        metadata_filter=metadata_filter,
        session_id=session_id
    )'''
    logger.debug(f"[{session_id}] rag-api req took {time.time()-start:.3f} secs")

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
    start = time.time()
    answer = await generate_reply(prompt)
    logger.debug(f"[{session_id}] llm answered in {time.time()-start:.3f} secs")

    # -----------------------------------------------------
    # Save conversation memory
    # -----------------------------------------------------
    start = time.time()
    save_chat(session_id, req.message, answer)
    logger.debug(f"[{session_id}] chat saved in {time.time()-start:.3f} secs")

    logger.debug(f"[{session_id}] Total API took {time.time()-api_start:.3f} secs")

    logger.info(f"Response completed | session={session_id}")
    if history:
        logger.debug(f"session id: {session_id} \n Question : {req.message} \n History Used : {history} \n Rewrriten Query : {rewritten_query}")

    logger.debug(f"session id: {session_id} \n Question:{req.message} \n Answer:{answer}")

    return {
        "answer": answer,
        "session_id": session_id,
        "sources": sources,
        "context": context
    }