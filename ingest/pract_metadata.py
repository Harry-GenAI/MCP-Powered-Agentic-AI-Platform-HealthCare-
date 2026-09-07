import re

#extract patient id / doctor id from ocr text

#document classification
def document_classification(file_name:str)->str:

    if "clinical" in file_name:
        return "clinical"
    
    if "admission" or "scanned" or "discharge" in filen_name:
        return "scanned"


#metadata builder
def metadata_builder(
    pdf_path:Path,
    text:str,
    has_images:bool,
    has_tables:bool,
    is_ocr:bool
)-> dict:
    
    document_type = document_classification(pdf_path.name)

    metadata = {
        "source":pdf_path,
        "doc_type":document_type
    }

    return metadata