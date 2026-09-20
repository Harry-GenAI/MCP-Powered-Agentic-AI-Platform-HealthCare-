# MCP-Powered Agentic AI Platform (HealthCare)

A production-style healthcare Agentic AI / Agentic RAG system combining
private hospital knowledge retrieval, MCP tools, LangGraph
orchestration, CrewAI agents, Human-in-the-Loop review, evidence
validation, Redis caching, PostgreSQL chat history, and a Streamlit
interface.

Architecture

```text
User Query
    ↓
FastAPI /chat
    ↓
Query Rewriter
    ↓
CrewAI Hospital AI Orchestrator
    ↓
LangGraph Conditional Routing
    ├── internal_rag
    │      ↓
    │   Weaviate Hybrid Search
    │      ↓
    │   CrossEncoder Reranking
    │      ↓
    │   Retrieval Confidence
    │      ├── sufficient ─────────→ Response
    │      └── insufficient + low risk
    │                    ↓
    │              MCP Web Search
    │                    ↓
    │                 Response
    │
    ├── vendor_rag ─────→ MCP Tool
    ├── query_database ─→ MCP SQLite Staff DB
    ├── web_search ─────→ MCP Web Search
    └── appointment ────→ MCP Appointment Tool
    ↓
High-Risk Requests
    ↓
Human-in-the-Loop Review
    ├── Approve
    ├── Modify
    └── Reject
    ↓
Evidence / Response Validator
    ↓
Final Answer

Redis ──→ safe completed-response cache
PostgreSQL ──→ chat history
SQLite ──→ staff DB + LangGraph checkpoints
```

## Features

- FastAPI `/chat` endpoint
- Streamlit healthcare chat and reviewer UI
- Query rewriting before orchestration
- CrewAI Hospital AI Orchestrator
- LangGraph conditional workflow orchestration
- Request classification: `clinical`, `business`, `appointment`, `general`
- Risk classification: `low`, `high`
- Internal RAG with Weaviate hybrid retrieval and CrossEncoder reranking
- Top-k context selection with source/page metadata
- Retrieval-confidence based fallback
- MCP tool integration
- Vendor/supplier RAG route
- Structured hospital staff database querying
- Controlled public web-search fallback for low-risk requests
- Appointment booking workflow
- Human-in-the-Loop using LangGraph `interrupt()`
- Separate `/review` resume flow
- Approve / modify / reject reviewer decisions
- Evidence and response validation
- Retry handling for invalid responses
- PostgreSQL chat history
- Redis caching for safe completed responses
- Local LangGraph checkpoint persistence
- Optional vLLM + Prometheus/Grafana GPU telemetry

## Validation Screenshots

### Appointment Booking

![Streamlit appointment booking](git_screenshots/streamlit_appointment.jpeg)

### Risk Level — Streamlit

![Streamlit risk-level routing](git_screenshots/streamlit_risk_lvl.jpeg)

### Risk Level — Terminal

![Terminal risk-level routing](git_screenshots/risk_lvl_terminal.jpeg)

### Grafana — Query Rewrite Metrics

![Grafana metrics after query rewriting](git_screenshots/metrics_after_updating_query_rewrite.png)

### Grafana — 100 VU Load Test

![Grafana 100 VU API and vLLM latency dashboard](git_screenshots/with_100_vus.png)

## High-Risk Human Review

High-risk requests are handled separately from normal response generation.

```text
High-risk request
      ↓
LangGraph
      ↓
Human Review interrupt
      ↓
Authorized reviewer
   ┌──┼──┐
Approve Modify Reject
   ↓     ↓     ↓
Final  Final  Rejection
Answer Answer

The reviewer supplies the final answer for approved or modified
requests. The workflow does not simulate a human reviewer with another
LLM.

Routing Logic

internal_rag

Hospital clinical knowledge, procedures, policies, operations,
departments, protocols, and internal references.

vendor_rag

Vendor/supplier information including products, equipment,
specifications, warranties, contracts, service information, and
procurement knowledge.

query_database

Structured hospital staff information such as doctors, nurses, lab
technicians, departments, shifts, availability, rooms, and leave status.

web_search

Current public external information. When internal RAG is insufficient,
web fallback is used for low-risk requests.

RAG sufficient
    ↓
Response

RAG insufficient + low risk
    ↓
MCP Web Search
    ↓
Response

High risk
    ↓
Human Review

High-risk requests do not bypass Human Review because internal retrieval
was insufficient.

MCP Tools

The MCP server provides controlled access to:

query_database

web_search

vendor_rag

book_appointment

send_email

text_cleaner

Internal RAG is executed directly by LangGraph rather than exposed as an
MCP tool.

Web Search

The web-search tool retrieves public search results and passes the
returned evidence to the response-generation stage.

The current implementation uses DuckDuckGo search through the ddgs
package rather than depending on fragile HTML result selectors.

Validation

The Evidence and Response Validator checks that the generated answer:

addresses the user query

is supported by available evidence

does not introduce unsupported claims

is clear and professionally formatted

Invalid responses enter the retry path up to the configured limit. Retry
exhaustion returns a safe fallback response.

Persistence and Caching

PostgreSQL

Conversation and chat-history storage.

Redis

Safe completed-response caching.

Redis is intentionally not used to bypass stateful Human-in-the-Loop
execution.

SQLite

Used for the hospital staff database and local LangGraph checkpoint
persistence.

Project Structure

Project-II/
├── api/
│   └── chat.py
├── graph/
│   ├── agents.py
│   ├── tasks.py
│   ├── state.py
│   ├── workflow.py
│   ├── routers.py
│   └── nodes/
│       ├── orchestrator.py
│       ├── rag.py
│       ├── tool.py
│       ├── response.py
│       ├── human_review.py
│       ├── validator.py
│       ├── appointment.py
│       ├── rejection.py
│       ├── retry.py
│       └── retry_exhausted.py
├── mcp_tools/
│   ├── mcp_server.py
│   └── mcp_client.py
├── rag/
│   └── rag.py
├── prompts/
│   └── prompts.py
├── memory/
├── middleware/
├── database/
├── docs/
├── staff.db
├── main.py
├── streamlit.py
├── requirements.txt
└── README.md

Environment

Create .env from .env.example.

DB_url=postgresql://username:password@host:5432/database_name
HF_token=hf_your_token_here
OpenAI_KEY=sk_your_openai_key_here

Never commit .env or private credentials.

Local Setup

pip install -r requirements.txt
uvicorn main:app --reload

In another terminal:

streamlit run streamlit.py

Human-in-the-Loop Test

The graph can also be tested directly:

python graph/test_graph.py

The CLI flow is:

Graph execution
      ↓
High-risk request
      ↓
LangGraph interrupt
      ↓
Review payload
      ↓
approve / modify / reject
      ↓
Command(resume=...)
      ↓
same checkpoint/thread resumes

API Flow

Chat

POST /chat

Starts the workflow. A high-risk request can return review_required
with the review payload.

Review

POST /review

Resumes the paused LangGraph thread using the same session/thread and
reviewer decision.

Supported decisions:

approve
modify
reject

GPU / vLLM Serving

The project can also be used with a vLLM serving path in a GPU
environment.

vllm serve local_model \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name private-llm

Verify:

curl http://localhost:8000/v1/models
curl http://localhost:8000/metrics

Prometheus and Grafana Telemetry

Useful inference metrics include:

vllm:num_requests_running
vllm:kv_cache_usage_perc
vllm:request_success_total
vllm:e2e_request_latency_seconds_count
http_requests_total

Key Engineering Decisions

LangGraph owns workflow state and conditional routing.

CrewAI provides specialized agent/task execution.

MCP provides controlled access to external tools.

Internal RAG is a dedicated retrieval worker.

Retrieval confidence controls low-risk fallback.

High-risk requests are gated by Human-in-the-Loop review.

Human review uses LangGraph interrupt() and checkpoint resume.

Redis caches only safe completed responses.

Evidence validation happens before low-risk responses are finalized.

The system separates orchestration, retrieval, tool execution,
response generation, validation, and review.

Git Notes

Keep the following ignored:

.env
venv/
.venv/
__pycache__/
local_model/
local_model.zip
*.db
```
