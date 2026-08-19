import fitz
import pdfplumber
import pytesseract

from pathlib import Path
from PIL import Image
from io import BytesIO
import re


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

project_root = Path(__file__).resolve().parent
docs_dir = project_root / "docs"
output_dir = project_root / "pract_output"


# ============================================================
# 1) Digital PDF Extraction
# ============================================================

def extract_digital_text(
    page
) -> str:

    return page.get_text(
        "text"
    ).strip()


# ============================================================
# 2) OCR Extraction
# ============================================================

def extract_ocr_text(
    page
) -> str:

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(
            2,
            2
        ),
        alpha=False
    )

    image = Image.open(
        BytesIO(
            pixmap.tobytes("png")
        )
    )

    return pytesseract.image_to_string(
        image
    ).strip()


# ============================================================
# 3) Extract + Save Actual Embedded Images
# ============================================================

def save_embedded_images(
    pdf_path: Path
) -> dict:

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    document = fitz.open(
        pdf_path
    )

    image_paths_by_page = {}

    for page_number, page in enumerate(
        document,
        start=1
    ):

        images = page.get_images(
            full=True
        )

        for image_number, image_info in enumerate(
            images,
            start=1
        ):

            xref = image_info[0]

            image_data = document.extract_image(
                xref
            )

            extension = image_data["ext"]

            output_file = (
                output_dir
                / (
                    f"{pdf_path.stem}"
                    f"_page{page_number}"
                    f"_image{image_number}."
                    f"{extension}"
                )
            )

            output_file.write_bytes(
                image_data["image"]
            )

            # IMPORTANT:
            # create the page list before append
            image_paths_by_page.setdefault(
                page_number,
                []
            ).append(
                str(output_file)
            )

            print(
                f"Saved image: {output_file}"
            )

    document.close()

    return image_paths_by_page


# ============================================================
# 4) Extract Tables By Page
# ============================================================

def _extract_tables_by_page(
    pdf_path: Path
) -> list[dict]:

    tables = []

    try:

        with pdfplumber.open(
            pdf_path
        ) as pdf:

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                page_tables = page.extract_tables()

                for table in page_tables:

                    if not table:
                        continue

                    tables.append(
                        {
                            "page": page_number,
                            "rows": table,
                        }
                    )

    except Exception as exc:

        print(
            f"Table extraction warning: {exc}"
        )

    return tables


# ============================================================
# 5) Extract Tables As Plain Text
# ============================================================

def extract_tables(
    pdf_path: Path
) -> str:

    tables = _extract_tables_by_page(
        pdf_path
    )

    formatted_rows = []

    for table in tables:

        rows = table["rows"]

        if not rows:
            continue

        headers = [
            str(cell or "").strip()
            for cell in rows[0]
        ]

        row_texts = []

        for row in rows[1:]:

            clean_row = [
                str(cell or "").strip()
                for cell in row
            ]

            row_lines = []

            for header, value in zip(
                headers,
                clean_row
            ):

                if header and value:

                    row_lines.append(
                        f"{header}: {value}"
                    )

            if row_lines:

                row_texts.append(
                    "\n".join(
                        row_lines
                    )
                )

        if row_texts:

            formatted_rows.append(
                f"[PAGE:{table['page']}]\n"
                + "\n\n".join(
                    row_texts
                )
            )

    return "\n\n".join(
        formatted_rows
    )


# ============================================================
# 6) Text Cleaning
# ============================================================

def clean_text(
    text: str
) -> str:

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
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

    text = re.sub(
        r"^[\s\.,;:\-]+",
        "",
        text
    )

    return text.strip()


# ============================================================
# 7) Remove Duplicate Table Content From Digital Text
# ============================================================

def remove_table_text_from_page(
    page_text: str,
    page_tables: list[dict]
) -> str:

    cleaned_page_text = page_text

    for table in page_tables:

        rows = table["rows"]

        if not rows:
            continue

        for row in rows[1:]:

            for cell in row:

                cell = str(
                    cell or ""
                ).strip()

                if not cell:
                    continue

                cell = clean_text(
                    cell
                )

                words = cell.split()

                if not words:
                    continue

                pattern = r"\s+".join(
                    re.escape(word)
                    for word in words
                )

                cleaned_page_text = re.sub(
                    pattern,
                    "",
                    cleaned_page_text,
                    flags=re.IGNORECASE
                )

    return clean_text(
        cleaned_page_text
    )


# ============================================================
# 8) Main PDF Parser
# ============================================================

def parse_pdf(
    pdf_path
) -> dict:

    pdf_path = Path(
        pdf_path
    )

    extracted_tables = (
        _extract_tables_by_page(
            pdf_path
        )
    )

    tables_by_page = {}

    for table in extracted_tables:

        tables_by_page.setdefault(
            table["page"],
            []
        ).append(
            table
        )

    pdf = fitz.open(
        pdf_path
    )

    page_texts = []

    total_images = 0
    is_ocr_used = False

    # --------------------------------------------------------
    # Process each page
    # --------------------------------------------------------

    for page_number, page in enumerate(
        pdf,
        start=1
    ):

        text = extract_digital_text(
            page
        )

        image_count = len(
            page.get_images(
                full=True
            )
        )

        total_images += image_count

        # ----------------------------------------------------
        # OCR fallback
        # ----------------------------------------------------

        if (
            len(text) < 50
            and image_count > 0
        ):

            text = extract_ocr_text(
                page
            )

            is_ocr_used = True

        text = clean_text(
            text
        )

        # ----------------------------------------------------
        # Remove duplicated table content
        # ----------------------------------------------------

        page_tables = tables_by_page.get(
            page_number,
            []
        )

        if page_tables:

            text = remove_table_text_from_page(
                text,
                page_tables
            )

        if text:

            page_texts.append(
                f"[PAGE:{page_number}]\n"
                f"{text}"
            )

    pdf.close()

    # --------------------------------------------------------
    # Save embedded images with page mapping
    # --------------------------------------------------------

    image_paths_by_page = {}

    if total_images > 0:

        image_paths_by_page = (
            save_embedded_images(
                pdf_path
            )
        )

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    table_text = extract_tables(
        pdf_path
    )

    has_tables = bool(
        table_text.strip()
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    final_text = "\n\n".join(
        page_texts
    )

    return {
        "text": final_text,
        "tables": table_text,
        "has_tables": has_tables,
        "has_images": total_images > 0,
        "image_paths_by_page": image_paths_by_page,
        "is_ocr": is_ocr_used,
    }