import streamlit as st
import os
import uuid
from services.memory.fetch_id import fetch_thread_ids
from ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config= Config()
        self.user_controls= {}

    def load_streamlit_ui(self):
        # Inject custom CSS for Figma-style colors
        
                
        st.set_page_config(page_title="🚦"+self.config.get_page_title(), layout="wide")
        st.header("🚦"+self.config.get_page_title())

        st.markdown("""
            <style>
                /* Background and font */
                body {
                    background-color: #f8f7fc;
                    color: #0e0e10;
                }

                /* Main container */
                .stApp {
                    background: linear-gradient(135deg, #f8f7fc, #e7e2f9);
                    color: #1a1a1a;
                    font-family: 'Segoe UI', sans-serif;
                }

                /* Sidebar styling */
                section[data-testid="stSidebar"] {
                    background-color: #f2e9fe; /* light purple */
                    color: #1a1a1a;
                }

                /* Input box */
                textarea, .stTextInput > div > input {
                    background-color: #ffffff;
                    color: #000;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                }

                /* Button */
                button[kind="primary"] {
                    background-color: #6d4eff;
                    color: white;
                    border-radius: 12px;
                    padding: 0.6em 1.2em;
                }

                button[kind="primary"]:hover {
                    background-color: #563bd8;
                }

                /* Tabs and headers */
                .stTabs [role="tablist"] {
                    background-color: #eee9fc;
                    border-radius: 12px;
                }

                h1, h2, h3, h4 {
                    color: #1a1a1a;
                }

                a {
                    color: #6d4eff;
                }
            </style>
        """, unsafe_allow_html=True)

        with st.sidebar:
            #options
            llm_options= self.config.get_llm_options()
            
            self.user_controls["selected_llm"]= st.selectbox("Select LLM",llm_options)
            self.user_controls["GROQ_API_KEY"]= st.session_state["GROQ_API_KEY"]=st.text_input("Groq API Key", type="password")
            self.user_controls["uploaded_pdf"]= st.file_uploader("Choose a PDF file.", type="pdf")
            if "ids" not in st.session_state:
                st.session_state.ids = fetch_thread_ids()
            new_session_request = st.checkbox("New Session")
            if(new_session_request):
                thread_id = str(uuid.uuid4())
                if thread_id not in st.session_state.ids:
                    st.session_state.ids= [thread_id] + st.session_state.ids

            self.user_controls["thread_id"]= st.selectbox("Select the thread ID", st.session_state.ids)

        return self.user_controls