from pdf_parser import parse_pdf
from pathlib import Path
from chunker import create_chunks

root = Path(__file__).resolve().parent.parent


parsed_data = parse_pdf(root/"docs/03_hospital_operations_reference.pdf")

#print(parsed_data, "\n\n", parsed_data["text"], "\n\n", parsed_data["tables"], "\n\n", parsed_data["image_paths_by_page"])

chunks = create_chunks(parsed_data["text"], parsed_data["tables"], {"document_type":"hospital_operations", "image_paths_by_page":parsed_data["image_paths_by_page"]})

for id, chunk in enumerate(chunks, start=1):

    print(f"\n id:{id}\n {chunk} \n\n")