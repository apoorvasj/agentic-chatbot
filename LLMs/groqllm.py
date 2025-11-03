import os
import streamlit as st
from langchain_groq import ChatGroq

class GroqLLM:
    """Initialise the model through Groq API"""
    def __init__(self,user_controls_input):
        #class variables
        self.user_controls_input= user_controls_input

    
    def get_llm_model(self):
        try:
            groq_api_key= self.user_controls_input["GROQ_API_KEY"]
            selected_groq_model= self.user_controls_input["selected_llm"]
            if groq_api_key=='' and os.environ["GROQ_API_KEY"]=='':
                st.error('Please enter the Groq API key.')

            print('PRINTING DETAILS')
            print(selected_groq_model, groq_api_key)

            llm= ChatGroq(model=selected_groq_model,api_key=groq_api_key,model_kwargs={
        "tool_choice": "none"       #This disables automatic tool calls
    })

        except Exception as e:
            raise ValueError(f'Error occurred with exception: {e}')
        return llm

