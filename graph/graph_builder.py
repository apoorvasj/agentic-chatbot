from state.state import State
from langgraph.graph import StateGraph, START, END
from nodes.chatbot_node import BasicChatbotNode
from services.services import decide_to_generate, correct_hallucination
from services.memory.postgres import create_checkpointer
from langgraph.checkpoint.postgres import PostgresSaver

class GraphBuilder:
    def __init__(self,model):
        self.llm= model
        self.graph_builder= StateGraph(State)

    def chatbot_build_graph(self):
        """
        Builds a chatbot graph using LangGraph. This method initialises a chatbot node using
        the 'BasicChatbotNode' class and integrates it into the graph. The chatbot node is set as
        both the entry and exit point of the graph.
        """
        self.basic_chatbot_node = BasicChatbotNode(self.llm)

        #add nodes
        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_node("retrieve", self.basic_chatbot_node.retrieve)
        self.graph_builder.add_node("grade_docs",self.basic_chatbot_node.grade_docs)
        self.graph_builder.add_node("rewrite",self.basic_chatbot_node.rewrite_query)
        self.graph_builder.add_node("check_hallucination", self.basic_chatbot_node.grade_hallucination)
        
        #add edges
        #self.graph_builder.add_edge(START, "retrieve")
        self.graph_builder.add_conditional_edges(START,self.basic_chatbot_node.route_question,
                                                 {
                                                     "vectordb": "retrieve",
                                                     "generate":"chatbot"
                                                 }
                                                 )
        self.graph_builder.add_edge("retrieve","grade_docs")
        self.graph_builder.add_conditional_edges("grade_docs",decide_to_generate,{
            "rewrite_query":"rewrite",
            "generate":"chatbot"
        })
        self.graph_builder.add_edge("rewrite","retrieve")
        self.graph_builder.add_edge("chatbot","check_hallucination")
        self.graph_builder.add_conditional_edges("check_hallucination", correct_hallucination,{
            "regenerate":"chatbot",
            "end":END
        })
        self.graph_builder.add_edge("chatbot",END)
        
        conn = create_checkpointer()
        print('Conn', conn)
        checkpointer= PostgresSaver(conn)
        
        #the below method only seems to work with with or context manager.
        #checkpointer= PostgresSaver.from_conn_string(DB_URI) 
        
        print('Checkpointer', checkpointer)
        checkpointer.setup()
        
        # Create a persistent connection
        #conn = psycopg.connect(DB_URI)

        # Initialize the checkpointer with the live connection
        #checkpointer = PostgresSaver(conn)
        #checkpointer.setup()
        return self.graph_builder.compile(checkpointer=checkpointer)
