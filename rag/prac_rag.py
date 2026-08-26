from rag import retrieve_context

while True:
    
    query = input("\n enter query: ")

    result = retrieve_context(query)

    print(
        f"\n retrieved docs:\n {result['retrieved_docs']}"
        f"\n\n top_docs:\n{result['top_docs']}"
        f"\n\n Context:\n{result['context']}"
        f"\n\n sources:\n{result['sources']}"
        f"\n\n retrieval_status:{result['retrieval_status']}"
        f"\n\n Score:{result['retrieval_score']}"
    )
