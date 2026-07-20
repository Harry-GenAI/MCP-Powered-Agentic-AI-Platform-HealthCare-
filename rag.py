from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sentence_transformers import CrossEncoder
import re
from logger import logger
import time


# Embedding model used for the persisted Chroma collection.
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load the persisted vector database.
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

# Cross-encoder reranker for document and sentence scoring.
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def compress_context(query, docs):
    start = time.time()
    sentences = []
    seen_sentences = set()

    for doc in docs:
        #looks for a period, exclamation, or question mark, but only splits if there is a space after it.
        lines = re.split(r'(?<=[.!?])\s+', doc.page_content)
        for line in lines:
            clean = line.strip()
            dedupe_key = re.sub(r'\s+', ' ', clean).lower().strip(".!?;:,")#explanation-I
            if clean and dedupe_key not in seen_sentences:
                seen_sentences.add(dedupe_key)
                sentences.append((clean, doc.metadata))

    if not sentences:
        return "", []

    pairs = [(query, sentence) for sentence, _ in sentences]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(sentences, scores),
        key=lambda x: x[1],
        reverse=True
    )

    threshold = 0.3
    top_sentences = [item for item in reranked if item[1] > threshold][:5]

    if not top_sentences:
        logger.info("context compression fallback activated..")
        top_sentences = reranked[:3]

    context = ""
    sources = []

    for (sentence, metadata), score in top_sentences:
        context += f"[source:{metadata.get('source')}]\n"
        context += sentence + "\n\n"
        source = metadata.get("source")
        if source:
            sources.append(source)

    logger.info(f"After context compressor, context built with '{len(top_sentences)}' sentences")
    
    return context, list(set(sources))


def retrieve_context(query, k=8, metadata_filter: dict | None = None, session_id=""):
    
    results = vector_db.similarity_search(query, k=k)
    

    #Metadata Filter
    filtered_docs = []

    for doc in results:
        if metadata_filter:
            match = all(
                doc.metadata.get(meta_key) == meta_value
                for meta_key, meta_value in metadata_filter.items()
            )
            if not match:
                continue

        filtered_docs.append(doc)

    if not filtered_docs:
        return "", []
    
    #ReRanker
    start = time.time()
    pairs = [(query, doc.page_content) for doc in filtered_docs]
    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(filtered_docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_docs = [doc for doc, score in reranked[:3]]
    
    context, sources = compress_context(query, top_docs)
    
    return context, sources, results