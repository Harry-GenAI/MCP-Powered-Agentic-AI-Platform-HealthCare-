from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from ingest import load_docs, create_chunks
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from logger import logger
from sentence_transformers import CrossEncoder
import re

#preprcessing fun/clean text

#embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#load vdb
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model,
)

#Build BM25
logger.info("Loading documents for BM25 retriever...")

docs = load_docs()

logger.info("Creating Chunks")

chunks = create_chunks(docs)

logger.info("Creating BM25 retriever")

bm25_retriever = BM25Retriever.from_documents(chunks)

bm25_retriever.k = 8


#Chroma Retriever
logger.info("Creating Chroma Retriever...")

dense_retriever = vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k":8}
)


#Hybrid Search
logger.info("Creating Ensemble Retriever...")

ensemble_retriever = EnsembleRetriever(
    retrievers=[
        dense_retriever,
        bm25_retriever
    ],
    weights=[
        0.5,
        0.5
    ]
)

#Metadata Filtering
def apply_metadata_filter(

    docs,

    metadata_filter=None

):

    if metadata_filter is None:

        return docs


    filtered_docs = []


    for doc in docs:

        matched = all(

            doc.metadata.get(key) == value

            for key, value in metadata_filter.items()

        )


        if matched:

            filtered_docs.append(doc)


    logger.info(

        f"Metadata Filter : {len(filtered_docs)} documents selected."

    )


    return filtered_docs


#cross encoder
logger.info("Loading CrossEncoder...")

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

#build context
def build_context(top_docs):

    context = ""
    sources = []

    seen_sources = set()

    for doc in top_docs:

        context += f"[source:{doc.metadata.get('source')}]\n"
        context += doc.page_content.strip()
        context += "\n\n"

        source = doc.metadata.get("source")

        if source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)

    logger.info(f"Context built with {len(top_docs)} chunks")

    return context, sources


#retrieve fun
def retrieve_context(query, metadata_filter:dict | None = None):

    #Hybrid Retrieval:
    retrieved_docs = ensemble_retriever.invoke(query)

    #metadata filter
    filtered_docs = apply_metadata_filter(retrieved_docs, metadata_filter)

    if not filtered_docs:
        logger.warning("No documents found after metadata filtering..")

        return "No relevant compnay knowledge found", [], [], []

    #reranker
    
    pairs = [(query, doc.page_content) for doc in filtered_docs]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(filtered_docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_docs = [doc for doc, score in reranked[:3]]
    
    context, sources = build_context(top_docs)

    logger.info("Hybrid Retrieval Completed Successfully.")

    return context, sources, retrieved_docs, top_docs

    