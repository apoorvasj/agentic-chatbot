from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

#Data Model

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: Literal["yes","no"]= Field(
        description="Documents are relevant to the question, 'yes' or 'no' "
    )

def grade_documents(llm):
    #LLM with function call
    structured_llm_grader= llm.with_structured_output(GradeDocuments)

    #Prompt
    system="""You are a grader assessing relevance of retrieved document to a user question.
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
    Output format (strictly): "yes" or "no"
    """

    grade_prompt = ChatPromptTemplate.from_messages([
        ("system",system),
        ("human", "Retrieved document: {document}. User question: {question}")
    ])

    retrieval_grader= grade_prompt|structured_llm_grader
    return retrieval_grader