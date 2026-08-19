from rag import retrieve_context

while True:
    
    query = input("\n enter query: ")

    retrieved_docs, top_docs, context, sources = retrieve_context(query)

    print(f"\n retrieved docs:\n {retrieved_docs} \n\n top_docs:\n{top_docs} \n\n Context:\n{context} \n\n sources:\n{sources}")