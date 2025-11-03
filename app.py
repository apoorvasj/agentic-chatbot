import streamlit as st
from ui.streamlitui.loadui import LoadStreamlitUI
from LLMs.groqllm import GroqLLM
from graph.graph_builder import GraphBuilder
from ui.streamlitui.displayresult import DisplayResultStreamlit
from services.services import upload_doc, load_vectorstore
from dotenv import load_dotenv

def load_agentic_app():
    """
    Load and run the Langgraph agentic AI app with streamlit UI.
    """

    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    load_dotenv(dotenv_path='../../.env')
    

    if(not user_input):
        st.error("Error: Failed to load the user input from UI")
        return
    
    #retrieve the document and call RAG on it.
    uploaded_file= user_input["uploaded_pdf"]

    if(uploaded_file):
        #call upload file function to save our file to local system.
        
        
        upload_doc(uploaded_file)
        load_vectorstore()
        
        user_message= st.chat_input("Enter your message:")
        thread_id = user_input["thread_id"]

        
        if user_message:
            
            #Configure LLM instance
            llm_config= GroqLLM(user_controls_input=user_input)

            #load model
            llm= llm_config.get_llm_model()

            if not llm:
                st.error("Error: LLM model could not be initialised.")
                return 
            #Initialise and set up the graph 
            graph_builder= GraphBuilder(llm)

            print('User message is ', user_message)
            graph= graph_builder.chatbot_build_graph()

            #Get the PNG bytes from the LangGraph graph
            png_bytes = graph.get_graph(xray=True).draw_mermaid_png()
            st.image(png_bytes, caption="LangGraph Mermaid Diagram")

            DisplayResultStreamlit(graph,user_message).display_result_on_ui(thread_id)
            
            
        

if __name__=='__main__':
    load_agentic_app()