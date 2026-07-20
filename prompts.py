
def build_prompt(context: str, question: str) -> str:
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a professional assistant. Answer ONLY using this context:

{context}

<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
