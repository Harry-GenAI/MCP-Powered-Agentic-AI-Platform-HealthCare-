# Project-02-Private LLM RAG System

A private RAG application that ingests PDF documents, stores embeddings in ChromaDB, retrieves relevant context, and serves answers from a locally saved Hugging Face causal language model. The project also includes a vLLM serving path with Prometheus and Grafana telemetry for GPU studio deployments.

## Features

- FastAPI `/chat` endpoint for RAG responses
- PDF ingestion pipeline with text cleaning and chunking
- ChromaDB vector store persisted locally
- Local Hugging Face model download via `save_model.py`
- vLLM OpenAI-compatible model server
- Prometheus metrics scraping from vLLM `/metrics`
- Grafana dashboard support through Prometheus

## Project Structure

- `main.py` - FastAPI app and `/chat` endpoint
- `ingest.py` - PDF loading, chunking, embeddings, and ChromaDB index creation
- `rag.py` - Retrieval, reranking, and context compression
- `llmservice.py` - Local model loading and response generation
- `query_rewriter.py` - Optional OpenAI-based query rewriting
- `db.py` - PostgreSQL chat history storage
- `save_model.py` - Downloads and saves the local model
- `telemetry/` - Prometheus and Grafana Docker Compose setup
- `docs/` - Source PDFs used for ingestion

## Environment

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Required values:

```env
DB_url=postgresql://username:password@host:5432/database_name
HF_token=hf_your_token_here
OpenAI_KEY=sk_your_openai_key_here
```

Never commit `.env`. It contains private credentials.

## Local Setup

```bash
pip install -r requirements.txt
python save_model.py
python ingest.py
uvicorn main:app --reload
```

## LightningAI vLLM Setup

Install dependencies:

```bash
pip install -r requirements.txt
pip install vllm
pip install -U scipy scikit-learn pandas matplotlib
pip check
```

Recreate ignored local assets inside the Studio:

```bash
python save_model.py
python ingest.py
```

Start vLLM from the project root:

```bash
vllm serve local_model --host 0.0.0.0 --port 8000 --served-model-name private-llm
```

Verify vLLM:

```bash
curl http://localhost:8000/v1/models
curl http://localhost:8000/metrics
```

## Telemetry

Start Prometheus and Grafana:

```bash
cd telemetry
docker compose up -d
```

Prometheus listens on port `19090` to avoid LightningAI proxy conflicts:

```bash
curl http://127.0.0.1:19090/api/v1/targets
```

Grafana runs on port `3000`. In LightningAI, expose/open port `3000`, then login:

```text
username: admin
password: admin
```

Add a Prometheus data source in Grafana:

```text
http://127.0.0.1:19090
```

Useful vLLM metrics:

```text
vllm:num_requests_running
vllm:kv_cache_usage_perc
vllm:request_success_total
vllm:e2e_request_latency_seconds_count
http_requests_total
```

## Validation Screenshots

Project validation screenshots are stored in `git_screenshots/`.

### FastAPI Swagger

![FastAPI Swagger UI](git_screenshots/fastapi_swagger.png)

### vLLM Server

![vLLM server running](git_screenshots/vllm.png)

### Grafana Query Rewrite Optimization

![Grafana metrics after updating standalone query rewriting](git_screenshots/metrics_after_updating_query_rewrite.png)

### Grafana 100 VU Load Test

![Grafana 100 VU API and vLLM latency dashboard](git_screenshots/with_100_vus.png)

## Future Upgrades

- Deploy the RAG stack on AWS EKS using Helm charts for repeatable Kubernetes releases.
- Benchmark larger local models beyond the current 1B setup, starting with 3B or 5B models and moving toward a 7B model when GPU resources allow.
- Add automated evaluation with RAG quality metrics such as faithfulness, context relevance, and answer correctness.
- Improve production readiness with CI/CD, health checks, autoscaling, and centralized logging.

## Git Notes

The following are intentionally ignored because they are private, generated, or too large for Git:

- `.env`
- `venv/` and `.venv/`
- `local_model/`
- `local_model.zip`
- `chroma_db/`
- `chroma_db_backup_*/`
- `__pycache__/`
- `core-key.pem`
