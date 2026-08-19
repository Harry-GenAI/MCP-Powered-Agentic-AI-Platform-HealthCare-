#extrat tables
import pdfplumber

from pathlib import Path



root = Path(__file__).resolve().parent.parent

def extract_tables_by_page(pdf_path:Path)->list[dict]:



    tables = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start = 1):

            page_tables = page.extract_tables()

            for table in page_tables:

                if not table:
                    continue

                tables.append(
                    {
                        "page":page_num,
                        "rows":table
                    }
                )
    
    return tables

pdf_path = root / "docs/01_clinical_knowledge_reference.pdf"

tables = extract_tables_by_page(pdf_path)

print(tables)






