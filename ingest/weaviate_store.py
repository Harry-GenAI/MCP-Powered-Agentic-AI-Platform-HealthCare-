import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timezone

import weaviate

from weaviate.classes.config import (
    Configure,
    Property,
    DataType,
)

from utils.logger import logger

from langchain_huggingface import (
    HuggingFaceEmbeddings,
)


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


MANIFEST_PATH = (
    PROJECT_ROOT
    / "weaviate_ingestion_manifest.json"
)


COLLECTION_NAME = (
    "MAOSDocuments"
)


# ============================================================
# Embedding Model
# ============================================================

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# ============================================================
# Manifest
# ============================================================

def load_manifest() -> dict:

    if not MANIFEST_PATH.exists():

        return {}


    try:

        with MANIFEST_PATH.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except Exception:

        logger.warning(
            "Manifest could not be loaded. "
            "Starting fresh."
        )

        return {}


def save_manifest(
    manifest: dict
):

    with MANIFEST_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2
        )


# ============================================================
# File Hash
# ============================================================

def calculate_file_hash(
    pdf_path: Path
) -> str:

    sha = hashlib.sha256()


    with pdf_path.open(
        "rb"
    ) as file:

        for data in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            sha.update(
                data
            )


    return sha.hexdigest()


# ============================================================
# Weaviate Connection
# ============================================================

def connect_weaviate():

    import os


    url = os.getenv(
        "WEAVIATE_URL"
    )

    api_key = os.getenv(
        "WEAVIATE_API_KEY"
    )


    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------

    if url and api_key:

        logger.info(
            "Connecting to Weaviate Cloud..."
        )


        return (
            weaviate
            .connect_to_weaviate_cloud(
                cluster_url=url,
                auth_credentials=(
                    weaviate.auth.Auth.api_key(
                        api_key
                    )
                ),
            )
        )


    # --------------------------------------------------------
    # Local
    # --------------------------------------------------------

    logger.info(
        "Connecting to local Weaviate..."
    )


    return weaviate.connect_to_local()


# ============================================================
# Collection
# ============================================================

def get_collection(
    client
):

    if not client.collections.exists(
        COLLECTION_NAME
    ):

        logger.info(
            f"Creating collection: "
            f"{COLLECTION_NAME}"
        )


        client.collections.create(

            name=COLLECTION_NAME,


            properties=[

                Property(
                    name="content",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="content_type",
                    data_type=DataType.TEXT
                ),

                Property(
                    name="source",
                    data_type=DataType.TEXT
                ),

                Property(
                    name="document_type",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="department",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="access_level",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="patient_id",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="doctor_id",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="document_version",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="ingestion_type",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="has_tables",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="has_images",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="image_paths",
                    data_type=DataType.TEXT_ARRAY
                ),

                Property(
                    name="page",
                    data_type=DataType.INT,
                ),

                Property(
                    name="chunk_index",
                    data_type=DataType.INT,
                ),

                Property(
                    name="source_hash",
                    data_type=DataType.TEXT,
                ),
            ],


            # We generate embeddings
            # ourselves using MiniLM.
            vector_config=(
                Configure.Vectors.self_provided()
            ),
        )


    return client.collections.use(
        COLLECTION_NAME
    )


# ============================================================
# Delete Existing Chunks
# ============================================================

def delete_old_objects(
    collection,
    object_ids: list[str],
):

    for object_id in object_ids:

        try:

            collection.data.delete_by_id(
                object_id
            )

        except Exception as exc:

            logger.warning(
                f"Could not delete "
                f"{object_id}: {exc}"
            )


# ============================================================
# Insert New Chunks
# ============================================================

def insert_chunks(
    collection,
    chunks,
    embeddings,
    source_hash,
):

    object_ids = []


    with collection.batch.fixed_size(
        batch_size=100
    ) as batch:


        for chunk, vector in zip(
            chunks,
            embeddings
        ):

            chunk_index = (
                chunk.metadata[
                    "chunk_index"
                ]
            )


            # Same source + same hash +
            # same chunk = deterministic ID
            object_id = str(
                uuid.uuid5(

                    uuid.NAMESPACE_URL,

                    (
                        f"{chunk.metadata['source']}"
                        f":{source_hash}"
                        f":{chunk_index}"
                    ),
                )
            )


            properties = {

                "content":
                    chunk.page_content,
                
                "content_type":
                      chunk.metadata.get("content_type", ""),

                "source":
                    chunk.metadata[
                        "source"
                    ],

                "document_type":
                    chunk.metadata[
                        "document_type"
                    ],

                "department":
                    chunk.metadata[
                        "department"
                    ],

                "access_level":
                    chunk.metadata[
                        "access_level"
                    ],

                "patient_id":
                    chunk.metadata[
                        "patient_id"
                    ],

                "doctor_id":
                    chunk.metadata[
                        "doctor_id"
                    ],

                "document_version":
                    chunk.metadata[
                        "document_version"
                    ],

                "ingestion_type":
                    chunk.metadata[
                        "ingestion_type"
                    ],

                "has_tables":
                    chunk.metadata[
                        "has_tables"
                    ],

                "has_images":
                    chunk.metadata[
                        "has_images"
                    ],
                
                "image_paths":
                     chunk.metadata.get("image_paths", []),

                "page":
                    int(
                        chunk.metadata.get(
                            "page",
                            0
                        )
                    ),

                "chunk_index":
                    int(
                        chunk_index
                    ),

                "source_hash":
                    source_hash,
            }


            batch.add_object(

                properties=properties,

                vector=vector,

                uuid=object_id,
            )


            object_ids.append(
                object_id
            )


    return object_ids


# ============================================================
# Process One Document
# ============================================================

def process_document(
    collection,
    pdf_path,
    chunks,
    manifest,
):

    source = pdf_path.name


    # --------------------------------------------------------
    # Calculate current file hash
    # --------------------------------------------------------

    current_hash = (
        calculate_file_hash(
            pdf_path
        )
    )


    previous = manifest.get(
        source
    )


    # --------------------------------------------------------
    # Unchanged document
    # --------------------------------------------------------

    if (
        previous
        and previous.get(
            "file_hash"
        ) == current_hash
    ):

        logger.info(
            f"SKIP | unchanged | "
            f"{source}"
        )

        return 0


    # --------------------------------------------------------
    # Modified document
    # --------------------------------------------------------

    if previous:

        logger.info(
            f"UPDATE | modified | "
            f"{source}"
        )


        delete_old_objects(
            collection,

            previous.get(
                "object_ids",
                []
            ),
        )


    else:

        logger.info(
            f"NEW | {source}"
        )


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    texts = [
        chunk.page_content
        for chunk in chunks
    ]


    embeddings = (
        embedding_model.embed_documents(
            texts
        )
    )


    # --------------------------------------------------------
    # Insert into Weaviate
    # --------------------------------------------------------

    object_ids = insert_chunks(

        collection,

        chunks,

        embeddings,

        current_hash,
    )


    # --------------------------------------------------------
    # Update manifest
    # --------------------------------------------------------

    manifest[source] = {

        "file_hash":
            current_hash,

        "object_ids":
            object_ids,

        "chunks":
            len(chunks),

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


    logger.info(
        f"Indexed {len(chunks)} chunks | "
        f"{source}"
    )


    return len(chunks)