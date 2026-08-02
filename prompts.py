
def build_prompt(context: str, question: str) -> str:
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

- You are a professional assistant. 
- Answer ONLY using this context.
- If user asked a question with code for example: LV-103, and there is a code in context and any text of after then return the answer
  with that corresponding code text.
  
  Examples:
  
User : LV-101
Context :
LV-101
Annual Leave
Employees are entitled to 24 paid annual leave days every calendar year.
Unused annual leave may be carried forward up to 10 days.
Annual leave requires manager approval before the leave starts.

Assistant :
Its about Annual Leave.
Employees are entitled to 24 paid annual leave days every calendar year.
Unused annual leave may be carried forward up to 10 days.
Annual leave requires manager approval before the leave starts.


User : LV-103
Context :
Leave Code: LV-103
Sick Leave
Employees receive 12 paid sick leave days every year.
A medical certificate is required when sick leave exceeds two consecutive days.
Managers may request supporting medical documents

Assistant:
Its about Sick Leave
Employees receive 12 paid sick leave days every year.
A medical certificate is required when sick leave exceeds two consecutive days.
Managers may request supporting medical documents


  :

{context}

<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
