import streamlit as st

class DisplayResultStreamlit:
    def __init__(self, graph, user_message):
        self.user_message = user_message
        self.graph = graph

    def display_result_on_ui(self, thread_id):
        graph = self.graph
        user_message = self.user_message

        with st.chat_message("user"):
            st.write(user_message)
            
        # Pass plain string to graph
        config = {"configurable":{
            "thread_id": thread_id
        }}
        response = graph.invoke({'question':user_message},config=config)

        with st.chat_message("assistant"):
            st.write(response['generation'])
        with st.chat_message("human"):
            st.write(response)