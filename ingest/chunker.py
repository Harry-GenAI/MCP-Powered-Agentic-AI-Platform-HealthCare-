from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


# ============================================================
# Recursive Character Text Splitter
# ============================================================

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


# ============================================================
# Text Cleaning
# ============================================================

def clean_text(
    text: str
) -> str:

    text = re.sub(
        r"\r\n?",
        "\n",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# Detect Domain-Specific Code Boundaries
# ============================================================

def get_regex_pattern(
    document_type: str
) -> str | None:

    # Medical policy:
    # HCP-201 - MediBridge Essential Care Plan
    # HCP-314 - CareShield Family Hospital Plan

    if document_type == "medical_policy":

        return (
            r"(?m)^(?=[A-Z]{2,6}"
            r"-\d+\s+-\s+)"
        )

    # Clinical knowledge is table-driven.
    # Table rows are handled separately below.

    if document_type == "clinical_knowledge":

        return None

    # Admission / discharge:
    # Patient ID: P1001

    if document_type in (
        "admission_report",
        "discharge_report"
    ):

        return (
            r"(?m)^(?=Patient\s*ID"
            r"\s*[:=]\s*[A-Z0-9-]+)"
        )

    return None


# ============================================================
# Regex-Based Logical Chunking
# ============================================================

def split_by_regex(
    text: str,
    pattern: str
) -> list[str]:

    sections = re.split(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    return [
        section.strip()
        for section in sections
        if section.strip()
    ]


# ============================================================
# Create Chunks
# ============================================================

def create_chunks(
    text: str,
    table_text: str,
    metadata: dict
) -> list[Document]:

    final_chunks = []

    document_type = metadata.get(
        "document_type",
        "general"
    )

    image_paths_by_page = metadata.get(
        "image_paths_by_page",
        {}
    )
    
    #to avoid img path in each and every chunk while unpacking at the time of creating document
    base_metadata = {
    key: value
    for key, value in metadata.items()
    if key != "image_paths_by_page"
    }


    # ========================================================
    # 1) NORMAL / OCR TEXT
    # ========================================================

    text = clean_text(
        text
    )

    if text:

        # PDF parser puts [PAGE:n] before each page.
        page_blocks = re.findall(
            r"\[PAGE:(\d+)\]\n"
            r"(.*?)(?=\n\[PAGE:\d+\]\n|\Z)",
            text,
            flags=re.DOTALL
        )

        for page_number, page_text in page_blocks:

            page_number = int(
                page_number
            )

            page_text = clean_text(
                page_text
            )

            if not page_text:
                continue

            pattern = get_regex_pattern(
                document_type
            )

            if pattern:

                sections = split_by_regex(
                    page_text,
                    pattern
                )

            else:

                sections = [
                    page_text
                ]

            for section_index, section in enumerate(
                sections
            ):

                section = section.strip()

                if not section:
                    continue

                # ------------------------------------------------
                # Small section -> one chunk
                # ------------------------------------------------

                if len(section) <= 700:

                    final_chunks.append(
                        Document(
                            page_content=section,
                            metadata={
                                **base_metadata,
                                "content_type": "text",
                                "page": page_number,
                                "section_index": section_index,
                            },
                        )
                    )

                # ------------------------------------------------
                # Large section -> split first
                # ------------------------------------------------

                else:

                    sub_chunks = (
                        recursive_splitter.split_text(
                            section
                        )
                    )

                    for sub_chunk in sub_chunks:

                        content = clean_text(
                            sub_chunk
                        )

                        if not content:
                            continue

                        final_chunks.append(
                            Document(
                                page_content=content,
                                metadata={
                                    **base_metadata,
                                    "content_type": "text",
                                    "page": page_number,
                                    "section_index": section_index,
                                },
                            )
                        )


    # ========================================================
    # 2) TABLE TEXT
    # ========================================================

    table_text = clean_text(
        table_text
    )

    if table_text:

        # PDF parser puts [PAGE:n] before each page's tables.
        table_blocks = re.findall(
            r"\[PAGE:(\d+)\]\n"
            r"(.*?)(?=\n\[PAGE:\d+\]\n|\Z)",
            table_text,
            flags=re.DOTALL
        )

        for page_number, page_table_text in table_blocks:

            page_number = int(
                page_number
            )

            page_table_text = clean_text(
                page_table_text
            )

            # Each blank-line-separated table row becomes one logical table chunk.
            table_rows = [
                row.strip()
                for row in re.split(
                    r"\n\s*\n",
                    page_table_text
                )
                if row.strip()
            ]

            for table_index, row in enumerate(
                table_rows
            ):

                final_chunks.append(
                    Document(
                        page_content=row,
                        metadata={
                            **base_metadata,
                            "content_type": "table",
                            "page": page_number,
                            "table_index": table_index,
                        },
                    )
                )


    # ========================================================
    # 3) Chunk Index + Page-Specific Image Paths
    # ========================================================

    for index, chunk in enumerate(
        final_chunks
    ):

        chunk.metadata[
            "chunk_index"
        ] = index

        page_number = chunk.metadata.get(
            "page"
        )

        page_images = image_paths_by_page.get(
            page_number,
            []
        )

        chunk.metadata[
            "has_images"
        ] = bool(
            page_images
        )

        chunk.metadata[
            "image_paths"
        ] = page_images

    return final_chunks