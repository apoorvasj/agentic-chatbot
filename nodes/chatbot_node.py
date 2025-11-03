from state.state import State
from services.services import load_vectorstore, rag_chain, rewriter, clean_text
from services.retrieval_grader import grade_documents
from services.hallucination_grader import grade_hallucination_helper
from services.router import router
from langchain_core.output_parsers import StrOutputParser

class BasicChatbotNode:
    """
    Basic Chatbot implementation
    """

    def __init__(self,model):
        self.llm= model
    
    def process(self,state:State)->dict:
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """

        
        question= state['question']
        documents= state["documents"]
        generation= rag_chain(self.llm, documents, question)
        clean_generation = clean_text(generation)

        
        return { "generation":clean_generation}
    
    def retrieve(self,state:State):
        """
        Retriever node

        Args:
        state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """

        print("---RETRIEVE---")
        
        question= state['question']
        

        # Retrieval
        retriever= load_vectorstore()
        documents = retriever.invoke(question)
        doc_texts = [clean_text(doc.page_content) for doc in documents]
        return {"documents": doc_texts}
    
    def grade_docs(self,state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state(dict): Updates documents key with only filtered relevant documents.
        """

        question= state['question']
        documents= state["documents"]

        #Give a score for each doc.
        filtered_docs= []
        #create an instance of a retrieval grader.
        retrieval_grader= grade_documents(self.llm)
        for d in documents:
            score= retrieval_grader.invoke(
                {'question':question, 'document':d}
            )

            grade= score.binary_score
            
            if(grade=="yes"):
                filtered_docs.append(d)
        re_gen_req= "no" if filtered_docs else "yes"
        return {"documents": filtered_docs, "re_gen_required":re_gen_req}
    
    def rewrite_query(self,state:State):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """
        print('REWRITING QUERY')
        question= state['question']
        

        rewrite_query= rewriter(self.llm)
        
        better_question= rewrite_query.invoke({'question',question})

        return {'question': better_question}
    
    def grade_hallucination(self, state:State):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Decision for next node to call
        """

        
        documents = state["documents"]
        generation= state["generation"]

        grader= grade_hallucination_helper(self.llm)
        score= grader.invoke({
            "documents":documents, "generation": generation
        })
        grade= score.binary_score
        
        #if we have regenerated query 5 times, no need to continue further.
        limit = state.get("re_gen_limit", 0)
        if(limit>5):
            return{"hallucination_present":"no","re_gen_limit":state["re_gen_limit"]}

        return{"hallucination_present":grade, "re_gen_limit":limit+1}
    
    def route_question(self, state:State):
        """
        Determine whether the generation can be done based on user query or retrieval should happen first.

        Args: state(dict): The current graph state

        Returns:
            str: Decision for next node to call- vectordb or generate
        """

        question= state['question']
        question_router = router(self.llm)
        decision= question_router.invoke({'question':question})
        if(decision.datasource== "vectordb"):
            return "vectordb"
        
        elif(decision.datasource== "generate"):
            return "generate"





