from weaviate_store import load_manifest, connect_weaviate, get_collection
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

docs_dir = project_root / "docs"

from pdf_parser import parse_pdf






def load_docs():
    
    #load manifest
    
    manifest = load_manifest()
    
    #connect weaviate & get collection
    client = connect_weaviate()
    collection = get_collection(client)

    files = sorted(docs_dir.glob("*.pdf"))
    
    #process every doc in the folder
    for file in files:
        
        #pdf_parser
        parsed_document = parse_pdf(file)

        
        
        
        
        
        
        
        asdddddsswdddddssss
        
        
        
        
        
        
        
        sdfsadfASEASSSSSSSSSSSSSSSSSSSSSSS ASDFASDF sdfggg#metadata
        
        #add image_paths
        
        #chunker
        
        #insert chunks
        
        #save manifest
