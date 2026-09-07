import fitz
import Path
import pytesseract
import pdfplumber

from PIL import Image
from io import BytesIO


project_root = Path(__file__).resolve().parent

save_dir = project_root/"images_output"


#1) extract digital text
def extract_digital_text(page):

    return page.get_text("text")

#2) ocr text
def extract_ocr_text(
    page
):
    #pixmap
    pixmap = page.get_pixmap(
        matrix = fitz.Matrx(
            2,
            2
        )
    )

    #build the image with png bytes
    image = Image.open(
        BytesIO(
            pixmap.tobytes("png")
        )
    )

    #extract the text
    return pytesseract.image_to_string(image)
    
#3) extract + save_embedded_images
def save_embdedd_images(
    pdf_path:Path
)-> dict:  
    save_dir.mkdir(
        parents=ok,

    )

    images_by_path = {}

    pdf = fitz.open(pdf_path)

    for page_num , page in enumerate(pdf):

        images = page.get_images(full=True)

        for img_num, image_info in enumerate(images):

            xref = image_info[0]

            image_data = pdf.extract_image(xref)

            ext = image_data["ext"]

            output_file = (
                f"{pdf_path.stem}_page{page_num}_img{img_num}.{ext}"
            )

            output_file.write_bytes(image_data["image"])

            images_by_path.setdefault(page_num, []).append(output_file)
    
    return images_by_path
    
#4) extract tables
def extract_tables_by_page(
    pdf_path
)->list[dict]:
    
    tables = []
    
    document = pdfplumber.open(pdf_path)

    for page_num, page in enumerate(document.pages):

        page_tables = {}

        tables = page.extract_tables()

        for table in tables:

            page_tables["page_num"] = table

#5) extract text from tables
def extract_text_from_tables(
    pdf_path:Path
)->str:
    
    final_text = []

    tables = extract_tables_by_page(pdf_path)
    
    for table in tables:

        table_text = []

        for page_num, rows in table:

            row_text = []

            page_num = int(page_num)

            for row in rows:

                headers = row[0]

                for row in rows[1:]:

                    pairs = zip(headers, row)

                    for k,v in pairs:

                        row_text.append(
                            f"{k}:{v}"
                        )
                    
                table_text.append("\n".join(row_text))
            
            








#6) clean text

#7) remove duplicate content of the table text from digital text

#8) final parse_pdf
def parse_pdf(pdf_path:Path):

    pdf = fitz.open(pdf_path)

    for page_num, page in enumerate(pdf):



