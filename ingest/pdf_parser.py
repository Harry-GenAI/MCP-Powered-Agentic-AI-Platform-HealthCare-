import fitz
import pdfplumber
import pystessearact
from PIL import Image
from io import BytesIO


# ============================================================
# Digital PDF Extraction
# ============================================================

def extract_digital_text(page)->str:
    
    return page.get_text("text").strip()



# ============================================================
# OCR Extraction
# ============================================================
def extract_ocr_text(page)->str:

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(
            2,
            2
        ), alpha = False
    )

    image = Image.open(
        BytesIO(
            pixmap.tobytes("png")
        )
    )

    return pystessearact.image_to_string(
        image
    ).strip()



# ============================================================
# Table Extraction
# ============================================================

def extract_tables(pdf_path)->str:

    tables = []

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf.pages, start = 1):

                page_tables = page.extract_tables()

                for table_number, table in enumerate(page_tables, start = 1):

                    if not table:
                        continue

                    rows = []

                    for row in table:

                        clean_row = [str(cell or "").strip() for cell in row]

                        rows.append("|".join(clean_row))

                        tables.append(
                            f"\nTABLE"
                            f"{table_number}"
                            f"PAGE:{page_number}"
                            + "\n".join(rows)
                        )
    
    except Exception as e:

        print(
            f"Table extraction warning:{e}"
        )
    

    return "\n".join(tables)



# ============================================================
# Text Cleaning
# ============================================================

def clean_text(text:str)->str:

    text = text.replace("\r\n", "\n")

    text = text.replace("\r", "\n")


    #collapse spaces/tabs
    import re

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )



    #Avoid too many blanks
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )


    #Remove extraction garbage
    text = re.sub(
        r"^[\s\.,;:\-]+",
        "",
        text
    )



# ============================================================
# Main PDF Parser
# ============================================================



# --------------------------------------------------------
# Extract tables separately
# --------------------------------------------------------



# --------------------------------------------------------
# Combine content
# --------------------------------------------------------