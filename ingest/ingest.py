import sys
from pathlib import Path
from datetime import datetime
import time


# ============================================================
# Make project root importable
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.append(
        str(PROJECT_ROOT)
    )


from dotenv import load_dotenv

from utils.logger import logger

from pdf_parser import parse_pdf
from metadata import build_metadata
from chunker import create_chunks

from weaviate_store import (
    connect_weaviate,
    get_collection,
    load_manifest,
    save_manifest,
    process_document,
)


load_dotenv()


# ============================================================
# Paths
# ============================================================

DOCS_PATH = (
    PROJECT_ROOT
    / "docs"
)


# ============================================================
# Main Ingestion Pipeline
# ============================================================

def ingest_documents():

    logger.info("=" * 30)

    logger.info(
        "MAOS INGESTION PIPELINE STARTED"
    )

    logger.info("=" * 30)


    # ========================================================
    # Validate docs folder
    # ========================================================

    if not DOCS_PATH.exists():

        raise FileNotFoundError(
            f"Docs folder not found: {DOCS_PATH}"
        )


    pdf_files = sorted(
        DOCS_PATH.glob(
            "*.pdf"
        )
    )


    if not pdf_files:

        logger.warning(
            "No PDF files found."
        )

        return


    logger.info(
        f"Discovered {len(pdf_files)} PDF file(s)."
    )


    # ========================================================
    # Load incremental-ingestion manifest
    # ========================================================

    manifest = load_manifest()


    # ========================================================
    # Connect to Weaviate once
    # ========================================================

    with connect_weaviate() as client:

        if not client.is_ready():

            raise RuntimeError(
                "Weaviate is not ready."
            )


        logger.info(
            "Connected to Weaviate successfully."
        )


        collection = get_collection(
            client
        )


        total_chunks = 0


        # ====================================================
        # Process every document
        # ====================================================

        for pdf_file in pdf_files:

            try:

                logger.info(
                    f"Processing: {pdf_file.name}"
                )


                # ------------------------------------------------
                # PDF → text / OCR / tables / images
                # ------------------------------------------------

                parsed_document = parse_pdf(
                    pdf_file
                )


                if not parsed_document[
                    "text"
                ] and not parsed_document[
                    "tables"
                ]:

                    logger.warning(
                        f"No usable content found: "
                        f"{pdf_file.name}"
                    )

                    continue


                # ------------------------------------------------
                # Build metadata
                # ------------------------------------------------

                metadata = build_metadata(
                    pdf_file,
                    parsed_document["text"],
                    parsed_document["has_tables"],
                    parsed_document["has_images"],
                    parsed_document["is_ocr"],
                )


                # ------------------------------------------------
                # Temporary page → image mapping
                #
                # This is used by chunker.py to attach
                # only the correct page image(s) to each chunk.
                # ------------------------------------------------

                metadata[
                    "image_paths_by_page"
                ] = (
                    parsed_document[
                        "image_paths_by_page"
                    ]
                )


                # ------------------------------------------------
                # Create chunks
                #
                # text and table_text are intentionally
                # passed separately.
                # ------------------------------------------------

                chunks = create_chunks(
                    parsed_document["text"],
                    parsed_document["tables"],
                    metadata,
                )


                if not chunks:

                    logger.warning(
                        f"No chunks created: "
                        f"{pdf_file.name}"
                    )

                    continue


                logger.info(
                    f"Created {len(chunks)} chunks "
                    f"for {pdf_file.name}"
                )


                # ------------------------------------------------
                # Process / insert into Weaviate
                # ------------------------------------------------

                inserted_chunks = process_document(
                    collection,
                    pdf_file,
                    chunks,
                    manifest,
                )


                total_chunks += (
                    inserted_chunks
                )


            except Exception:

                logger.exception(
                    f"Failed to process "
                    f"{pdf_file.name}"
                )


        # ========================================================
        # Save manifest after all documents
        # ========================================================

        save_manifest(
            manifest
        )


        logger.info(
            f"Total chunks inserted: "
            f"{total_chunks}"
        )


    logger.info("=" * 30)

    logger.info(
        "MAOS INGESTION PIPELINE COMPLETED"
    )

    logger.info("=" * 30)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    start_time = time.time()

    ingest_documents()

    elapsed = time.time() - start_time

    logger.info(
        f"Ingestion completed in "
        f"{elapsed:.2f} seconds."
    )