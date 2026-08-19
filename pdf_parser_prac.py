import fitz
import pdfplumber
import pytesseract
from pathlib import Path
from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

project_root = Path(__file__).resolve().parent

docs_dir = project_root / "docs"

output_dir = project_root / "pract_output"


#1) digital pdf extraction
def extract_digital_text(page)->str:

    return page.get_text("text").strip()


#2) OCR for scanned images
def extract_ocr_text(page)->str:

    #render pdf pages into img
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(2,2),
        alpha=False
    )

    # img to png bytes
    image_bytes = pixmap.tobytes("png")

    #png bytes into in-memory img file
    image = Image.open(BytesIO(image_bytes))


    # extract the txt from that in-memory img file
    return pytesseract.image_to_string(image).strip()


#3) extract actual embded images
def save_embedded_images(pdf_path: Path):

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )
    
    #convert the pdf into Document
    document = fitz.open(pdf_path)
    

    for page in document:
        
        
        #get the images
        images = page.get_images(full=True)

        
        
        #extract the txt:
        for image_number, image_info in enumerate(images, start=1):

            #img ref inside pdf
            xref = image_info[0]

            #extract actual image
            image_data = document.extract_image(
            xref
            )

            extension = image_data["ext"]

            output_file = (
            output_dir / (
                f"{pdf_path.stem}"
                f"_image{image_number}."
                f"{extension}"

            )
            )

            output_file.write_bytes(
            image_data["image"]
            )
            
        
            
            print(
            f"Saved_image"
            f"{output_file}"
            )

            

        
    
    document.close()

#4) extract text in tables
def extract_tables(pdf_path:Path):

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            tables = page.extract_tables()

            for table_number, table in enumerate(tables, start=1):

                all_tables.append({
                    "page":page_number,
                    "table":table_number,
                    "rows" : table
                })
    
    return all_tables

# detect embd images
def get_img_count(page)->int:

    return len(page.get_images(full=True))

#5) inspect with 1 pdf:
def inspect_pdf(pdf_path:Path):

    print(f"\n {pdf_path.name} \n")

    document = fitz.open(pdf_path)

    #page by page inspect
    for page_number, page in enumerate(document, start=1):

        #extract text from digital pdf
        text = extract_digital_text(page)

        image_count = get_img_count(page)

        if text:
            print(f"\n page no:{page_number} \n digital charcs : {len(text)}, \n digital text preview:{text}")
        

        #detect scanned page
        if len(text) < 50 and image_count > 0:

            print(f"\n digital txt is missing, page appears img based , running OCR... actual text length is {len(text)}")

            ocr_txt = extract_ocr_text(page)

            print(f"\n ocr result : {ocr_txt} \n")
        
    document.close()
        
    #tables
    tables = extract_tables(pdf_path)
        
    print(f"\n tables deteced : {len(tables)} \n")

    for item in tables:

        print(
            f"\n Table :{item['table']}"
            f"\n on Page :{item['page']}"
        )

        for row in item['rows']:
            print(row)

#main
if __name__ == "__main__":
    
    pdf_files = [
        docs_dir/"01_clinical_knowledge_reference.pdf",
        docs_dir/ "02_medical_policy_reference.pdf",
        docs_dir
        / "03_hospital_operations_reference.pdf",

        docs_dir
        / "04_scanned_discharge_checklist_ocr.pdf",

    ]

    for file in pdf_files:

        inspect_pdf(file)

    #explicit image extraction:

    ops_pdf = docs_dir/"03_hospital_operations_reference.pdf"

    print("running text on image extraction....")

    save_embedded_images(ops_pdf)









