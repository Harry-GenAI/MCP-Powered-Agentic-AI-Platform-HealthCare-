import pymupdf
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

docs_dir = PROJECT_ROOT / "docs"

#digital text extraction
def extract_digital_text(page):
    
    return page.get_text("text").strip()

#ocr

#extract actual embedded images

#extract tables

#inspect pdf
def inspect_pdf(pdf_path:Path):

    print(f"\n {pdf_path.name}\n")

    document = pymupdf.open(pdf_path)

    #page by page inspect
    for page_number, page in enumerate(document, start=1):

        #extract digital text
        text = extract_digital_text(page)

        


#main
if __name__ == "__main__":

    files = [
         docs_dir/"01_clinical_knowledge_reference.pdf"
    ]

    for file in files:
        inspect_pdf(file)

