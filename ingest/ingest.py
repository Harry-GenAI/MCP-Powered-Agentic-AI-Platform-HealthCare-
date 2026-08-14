import sys
from pathlib import Path
from datetime import datetime, timezone


# ------------------------------------------------------------
# Make project root importable when running:
# python ingest/ingest.py
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
from utils.logger import logger



load_dotenv()

# ============================================================
# Paths
# ============================================================

DOCS_PATH = PROJECT_ROOT/"docs"


# ============================================================
# Main Ingestion Pipeline
# ============================================================

def ingest_documents():

    logger.info("=" * 30)
    logger.info("MAOS Ingestion PP Started...")
    logger.info("=" * 30)

    
    #Validate docs folder
    if not DOCS_PATH.exists():

        raise FileNotFoundError(
            f"Docs folder not found:{DOCS_PATH}"
        )

    pdf_files = sorted(
        DOCS_PATH.glob("*.pdf")
    )

    if not pdf_files:
        logger.warning("No PDF files found")
    
    
    return logger.info(f"Discovered {len(pdf_files)} PDF files.")


# --------------------------------------------------------
# Load incremental-ingestion manifest
# --------------------------------------------------------

manifest = load_manifest()


# --------------------------------------------------------
# Connect to Weaviate once
# --------------------------------------------------------



         #process every doc


         #pdf -> text/OCR/tables


         #build metadata


         #convert parsed content -> chunks


         #incremental weviate ingestion


         #save manifest






