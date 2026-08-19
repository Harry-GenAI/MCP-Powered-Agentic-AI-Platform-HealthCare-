import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

from weaviate.classes.query import Filter

from ingest.weaviate_store import (
    connect_weaviate,
    get_collection,
)

from utils.logger import logger


# ============================================================
# Configuration
# ============================================================

TOP_K = 8
FINAL_K = 3
HYBRID_ALPHA = 0.5


# ============================================================
# Embedding Model
# ============================================================

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# ============================================================
# Weaviate
# ============================================================

logger.info("Connecting to Weaviate...")

weaviate_client = connect_weaviate()

if not weaviate_client.is_ready():
    raise RuntimeError(
        "Weaviate is not ready."
    )

vector_db = get_collection(
    weaviate_client
)

logger.info(
    "Connected to Weaviate successfully."
)


# ============================================================
# Metadata Filtering
# ============================================================

def build_metadata_filter(
    metadata_filter: dict | None = None
):

    if not metadata_filter:
        return None

    filters = []

    for key, value in metadata_filter.items():

        filters.append(
            Filter.by_property(
                key
            ).equal(value)
        )

    if not filters:
        return None

    combined_filter = filters[0]

    for current_filter in filters[1:]:

        combined_filter = (
            combined_filter & current_filter
        )

    return combined_filter


# ============================================================
# Convert Weaviate Objects → LangChain Documents
# ============================================================

def convert_to_documents(
    objects
):

    docs = []

    for obj in objects:

        properties = obj.properties

        metadata = {
            key: value
            for key, value in properties.items()
            if key != "content"
        }

        docs.append(
            Document(
                page_content=properties.get(
                    "content",
                    ""
                ),
                metadata=metadata,
            )
        )

    return docs


# ============================================================
# CrossEncoder
# ============================================================

logger.info(
    "Loading CrossEncoder..."
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ============================================================
# Build Context
# ============================================================

def build_context(
    top_docs
):

    context = ""
    sources = []

    seen_sources = set()

    for doc in top_docs:

        source = doc.metadata.get(
            "source"
        )

        page = doc.metadata.get(
            "page"
        )

        context += (
            f"[source:{source} "
            f"page:{page}]\n"
        )

        context += (
            doc.page_content.strip()
        )

        context += "\n\n"

        if source not in seen_sources:

            seen_sources.add(source)

            sources.append(source)

    logger.info(
        f"Context built with "
        f"{len(top_docs)} chunks"
    )

    return context, sources


# ============================================================
# Retrieve Context
# ============================================================

def retrieve_context(
    query,
    metadata_filter: dict | None = None
):

    logger.info(
        "Starting Hybrid Retrieval..."
    )

    # --------------------------------------------------------
    # Query Embedding
    # --------------------------------------------------------

    query_vector = (
        embedding_model.embed_query(
            query
        )
    )

    # --------------------------------------------------------
    # Metadata Filter
    # --------------------------------------------------------

    weaviate_filter = (
        build_metadata_filter(
            metadata_filter
        )
    )

    # --------------------------------------------------------
    # Hybrid Search
    # --------------------------------------------------------

    response = vector_db.query.hybrid(

        query=query,

        vector=query_vector,

        alpha=HYBRID_ALPHA,

        limit=TOP_K,

        filters=weaviate_filter,

        return_properties=[
            "content",
            "content_type",
            "source",
            "document_type",
            "department",
            "access_level",
            "patient_id",
            "doctor_id",
            "document_version",
            "ingestion_type",
            "has_tables",
            "has_images",
            "image_paths",
            "page",
            "chunk_index",
            "source_hash",
        ],
    )

    retrieved_docs = (
        convert_to_documents(
            response.objects
        )
    )

    if not retrieved_docs:

        logger.warning(
            "No documents found."
        )

        return (
            "No relevant company "
            "knowledge found",
            [],
            [],
            [],
        )

    logger.info(
        f"Hybrid Retrieval returned "
        f"{len(retrieved_docs)} chunks."
    )

    # --------------------------------------------------------
    # Reranking
    # --------------------------------------------------------

    pairs = [
        (
            query,
            doc.page_content
        )
        for doc in retrieved_docs
    ]

    scores = reranker.predict(
        pairs
    )

    reranked = sorted(
        zip(
            retrieved_docs,
            scores
        ),
        key=lambda x: x[1],
        reverse=True,
    )

    # --------------------------------------------------------
    # Top-K Evidence
    # --------------------------------------------------------

    top_docs = [
        doc
        for doc, score in reranked[:FINAL_K]
    ]

    # --------------------------------------------------------
    # Build Context
    # --------------------------------------------------------

    context, sources = (
        build_context(
            top_docs
        )
    )

    logger.info(
        "Hybrid Retrieval Completed "
        "Successfully."
    )

    return (
        retrieved_docs,
        top_docs,
        sources,
        context
    )