from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

#Data model

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectordb","generate"] = Field(
        description= "Given a user question choose vectordb or generate."
    )

def router(llm):
    structured_llm_router= llm.with_structured_output(RouteQuery)

    #Prompt
    system= """You are an expert routing user question to a vectorstore. The vectorstore contains traffic regulations documents. Use the vectorstore
    for any traffic or road safety related questions. If summary is asked and otherwise, move to LLM generation.
    Strictly output vectorstore for vectorstore retrieval OR generate for message generation."""

    route_prompt = ChatPromptTemplate.from_messages([
        ("system",system),
        ("human","{question}")
    ])

    question_router= route_prompt | structured_llm_router
    return question_router

    