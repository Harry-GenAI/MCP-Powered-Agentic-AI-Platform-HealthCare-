from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from logger import logger
import os
import re
import shutil



#embed model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#clean text fun/pre-processing fun
def clean_text(text):
   #replacing the \n with space but not touching the "\n\n"
   text = re.sub(r'((?<!\n)\n(?!\n))', ' ', text)
   #collapse multiple spaces into one
   text = re.sub(r' +', ' ', text)
   #Fix removing any string started with . or any other special charcs after chunking
   text = re.sub(r'^[\.\,\-\:]+\s*', '', text)

   return text.strip()

#load_docs
def load_docs(folder="docs"):
   
   documents = []

   for file in os.listdir(folder):
      if not file.endswith(".pdf"):
         continue
      path = os.path.join(folder, file)
      loader = PyPDFLoader(path)
      docs = loader.load()

      #add metadata:
      for doc in docs:
         doc.metadata["source"]=file
         doc.metadata["doc_type"]=file.replace(".pdf","")
         doc.metadata["department"]="general"
      documents.extend(docs)
   return documents


#chunks
def create_chunks(docs):
   splitter = RecursiveCharacterTextSplitter(
      chunk_size=500,
      chunk_overlap=100,
      separators=["\n\n", ".", " "]
   )

   chunks = splitter.split_documents(docs)
   
   for chunk in chunks:
      chunk.page_content = clean_text(chunk.page_content) #to remove any string or pagecontent started with "."
   return chunks


#embd docs and add in vectordb (chroma)
def build_vectordb(chunks):
   if os.path.exists("./chroma_db"):
      shutil.rmtree("./chroma_db")

   texts = [chunk.page_content for chunk in chunks]
   metadatas=[chunk.metadata for chunk in chunks]

   vector_db=Chroma.from_documents(
      documents=chunks,
      embedding=embedding_model,
      persist_directory="./chroma_db",
      collection_metadata={"hnsw:space":"cosine"} #"hnsw":"cosine" will set the distance metric as cosine similarity
   )

   vector_db.persist()
   return vector_db


#main()
def main():
   logger.info("\n---ingestion pipeline started---")
   documents = load_docs()
   chunks = create_chunks(documents)
   build_vectordb(chunks)

   logger.info(f"\n\n----ingestion completed with {len(chunks)} chunks-----\n")
   
#entry-point guard
if __name__ == "__main__":
   main()



   


