import os
import re
import shutil

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from logger import logger

#Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# Load entire PDF as one document
def load_docs(folder="docs"):

    documents = []

    for file in os.listdir(folder):

        if not file.endswith(".pdf"):
            continue

        path = os.path.join(folder, file)

        logger.info(f"Loading {file}")

        loader = PyPDFLoader(path)

        pages = loader.load()

        # Merge all pages into one text
        full_text = "\n\n".join(
            page.page_content for page in pages
        )

        metadata = pages[0].metadata.copy()

        metadata["source"] = file
        metadata["doc_type"] = file.replace(".pdf", "")

        if "leave" in file:

            metadata["department"] = "hr"
            metadata["category"] = "leave"
            metadata["tags"] = "leave,annual leave,casual leave,sick leave,maternity,paternity"

        elif "travel" in file:

            metadata["department"] = "administration"
            metadata["category"] = "travel"
            metadata["tags"] = "travel,hotel,flight,reimbursement,transport"

        elif "remote" in file:

            metadata["department"] = "it"
            metadata["category"] = "remote_work"
            metadata["tags"] = "remote work,vpn,mfa,laptop,security"

        else:

            metadata["department"] = "general"
            metadata["category"] = "general"
            metadata["tags"] = "general"

        documents.append(

            Document(

                page_content=full_text,

                metadata=metadata

            )

        )

    logger.info(f"Loaded {len(documents)} complete documents")

    return documents


# ------------------------------------
# Regex Chunking
# ------------------------------------
def create_chunks(docs):

    chunks = []

    for doc in docs:

        text = doc.page_content

        source = doc.metadata["source"]

        if "leave" in source:
            pattern = r"(?=Leave Code:\s*LV-\d+)"

        elif "travel" in source:
            pattern = r"(?=Travel Code:\s*TR-\d+)"

        elif "remote" in source:
            pattern = r"(?=Remote Work Code:\s*RW-\d+)"

        else:
            pattern = None


        if pattern:
            sections = re.split(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        else:
            sections = [text]


        for section in sections:

            section = section.strip()

            if len(section) < 20:
                continue

            chunks.append(
                Document(
                    page_content=section.lower(),
                    metadata=doc.metadata.copy()
                )
            )

    logger.info(f"Created {len(chunks)} regex chunks")

    return chunks

# ------------------------------------
# Build Chroma VectorDB
# ------------------------------------
def build_vectordb(chunks):

    logger.info("Building Chroma Vector Database...")

    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="./chroma_db",
        collection_metadata={"hnsw:space": "cosine"},
    )

    logger.info("Vector DB Created Successfully.")

    return vector_db

# ------------------------------------
# main()
# ------------------------------------
def main():

    logger.info("------ Ingestion Started ------")

    docs = load_docs()

    chunks = create_chunks(docs)

    build_vectordb(chunks)

    logger.info(f"Total Documents : {len(docs)}")
    logger.info(f"Total Chunks    : {len(chunks)}")

    logger.info("------ Ingestion Completed ------")


#python safeguard
if __name__ =="__main__":
    main()