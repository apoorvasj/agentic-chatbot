import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from config.settings import CHUNK_OVERLAP, CHUNK_SIZE, HF_MODEL, TEMP_PDF_PATH, CH_MODEL
#from langchain_hub import hub
from langchain_core.output_parsers import StrOutputParser
from LLMs.groqllm import GroqLLM
from langchain_core.prompts import ChatPromptTemplate
from state.state import State
from dotenv import load_dotenv
from langsmith import Client
#from langchain_cohere import CohereEmbeddings
import os
from langchain_huggingface import HuggingFaceEmbeddings

"""
All the additional services required for the traffic regulations chatbot
such as RAG functionality. 
"""

def upload_doc(uploaded_file):
    file_path= TEMP_PDF_PATH
    print("File path is ",file_path)
    with open(file_path,"wb") as f:
        f.write(uploaded_file.getvalue())
    
@st.cache_resource
def load_vectorstore():
    """
    Function to process the PDF= load, split(chunking), embed and store in a vectorstore.

    Returns: A retriever
    """
    file_path= TEMP_PDF_PATH
    
    loader= PyPDFLoader(file_path)
    docs= loader.load()
    splitter= RecursiveCharacterTextSplitter(chunk_size= CHUNK_SIZE, chunk_overlap= CHUNK_OVERLAP)
    splitted= splitter.split_documents(docs)

    embeddings= HuggingFaceEmbeddings(
    model=HF_MODEL
)
    vectorstore= Chroma.from_documents(splitted, embeddings)

    #this query is for testing purposes.
    #query='pedestrians'
    #print(vectorstore.similarity_search(query))
    return vectorstore.as_retriever()

def rag_chain(llm, docs, question):
    #prompt = hub.pull("rlm/rag-prompt")
    load_dotenv(dotenv_path='../../.env')
    client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
    prompt = client.pull_prompt("rlm/rag-prompt", include_model=True)
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    generation = rag_chain.invoke({"context": docs, "question": question})
    print(generation)
    return generation

def rewriter(llm):

    system= """You a question re-writer that converts an input question to a better
    version that is optimized for web search. Look at the input and try to reason about the underlying semantic intent/ meaning."""

    re_write_prompt= ChatPromptTemplate.from_messages([
        ("system",system),
        (
            "human",
            "Here is the initial question. {question}. Formulate an improved question."
        )
    ])

    question_rewriter= re_write_prompt |llm | StrOutputParser()
    return question_rewriter

def decide_to_generate(state:State):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """
    
    decision = state.get("re_gen_required")
    if decision == "yes":
        return "rewrite_query"
    elif decision == "no":
        return "generate"
    else:
        raise ValueError(f"Unexpected or missing value for 're_gen_required': {decision}")
    
def correct_hallucination(state:State):
    """
    Determines whether the current generation has hallucination present.

    Args:
        state (dict): The current graph state
    
    Returns:
        str: Binary decision for next node to call
    """

    decision= state["hallucination_present"]
    if(decision== "yes"):
        return "regenerate"
    else:
        return "end"
    
def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")

