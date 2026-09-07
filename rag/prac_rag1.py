from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingest.weaviate_store import connect_weaviate, get_collection
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

from weaviate.classes.query import Filter

#configuration

TOP_K = 8,
FINAL_K = 3,
HYBRID_ALPHA = 0.5
RERANK_THRESHOLD = 0.5

#weaviate and load vdb

client = connect_weaviate()

vdb = get_collection(client)


#embedding model
embd_model = HuggingFaceEmbeddings("")

#build metadata filter
def build_metadata_filter(
    metadata_filter:dict
):
    filters = []

    for k,v in metadata_filter.items():
        filters.append(
            Filter.by_property(key).equal(value)
        )

        if not filters:
            return None
    
    combined_filter = filters[0]

    for current_filter in filters[1:]:
        combined_filter = (combined_filter & current_filter)
    
    return combined_filter
     
#convert objects into LC docs
def convert_obj( objects):

    docs = []

    for obj in objects:

        properties = obj.properties

        metadata = {
            k : v
            for k,v in properties.items()
            if k != "content"
        }
        
        from langchain_core.documents import Document
        
        docs.append(
            Document(
                page_content=properties.get("content", ""),
                metadata=metadata
            )
        )

        return docs


#cross encoder model
reranker = CrossEncoder("")

#build context
def build_context(
    top_docs
):
    return context, sources

#retrieve context 
def retrieve_context(
    query,
    metadata_filter:dict | None = None
)->dict:
    
    #embd query
    query_vector = embd_model.embed_query(query)

    #metadata filter
    metadata_filter = build_metadata_filter(metadata_filter)

    #hybrid search
    response = vdb.query.hybrid(
        query = query,
        vector=query_vector,
        alpha=HYBRID_ALPHA,
        limit=TOP_K,
        filters=metadata_filter,
        return_properties=[""]
    )

    objects = response.properties

    retrieved_docs = convert_obj(objects)

    #No retrieval results

    #reranking

    #best retrieval score
    top_score = reranked[0][1]

    #retrieval sufficiency check

    if top_score < RERANK_THRESHOLD:

        print("retrieval confidence is insufficient")

        return {
            "retrieved_docs":retrieved_docs,
            "context":[],
            "retrieval_status":"insufficient",
            "retrieval_score":top_score
        }
    
    #final k

    #build context

    return {
        "retrieved_docs":retrieved_docs,
        "context":context,
        "sources":sources,
        "retrieval_status":"sufficient"
    }

