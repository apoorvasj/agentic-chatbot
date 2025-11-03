import streamlit as st
import psycopg
from config.settings import DB_URI

def connect():
    """
    Establish database connection.
    """
    #"dbname= chatbot host = 127.0.0.1 user = postgres password=4455 port=5432"
    conn = psycopg.connect(       
        DB_URI)

    if conn:
        print("Connection established successfully.")
    else: 
        print("Failed to establish a connection.")
    return conn

@st.cache_data
def fetch_thread_ids():
    """
    Function to fetch all the thread IDs from the database.
    """

    conn= connect()
    try:
        with conn.cursor() as curr:
            curr.execute("SELECT DISTINCT(thread_id) FROM checkpoints")
            #print(curr.fetchall())
            ids= [str(row[0]) for row in curr.fetchall()]
            return ids
    except:
        return []
    
if __name__ == '__main__':
    fetch_thread_ids()