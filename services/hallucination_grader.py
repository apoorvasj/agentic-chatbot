from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

#Data Model for hallucination Grader

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generated answer."""

    binary_score: Literal["yes","no"]= Field(description="Answer is grounded in facts, yes or no")

#LLM with function call

def grade_hallucination_helper(llm):
    #LLM with function call

    structured_llm_grader= llm.with_structured_output(GradeHallucinations)

    prompt= ChatPromptTemplate.from_messages([
        ("system","""You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""),
     ("human","Set of facts: {documents} LLM generation: {generation}")
    
    ])
    

    hallucination_grader= prompt | structured_llm_grader
    return hallucination_grader
