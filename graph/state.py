from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import TypedDict


class AgentState(TypedDict, total=False):

    # User / Session
    user_query : str
    user_role : str
    conversation_history : list


    # Orchestration
    request_type: str
    route: str
    risk_level: str


    # RAG
    context : str
    sources : list
    retrieval_status : str


    # Tools  sql/websearch/External RAG
    tool_result : str


    # LLM Response
    draft_answer: str


    # Human Review
    review_status: str
    reviewer_feedback: str
    modified_answer: str



    # Validation
    validation_status : str
    validation_reason : str


    # Final response
    final_answer : str


    #Retry / control
    retry_count : int