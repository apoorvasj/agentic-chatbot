from langgraph.checkpoint.postgres import PostgresSaver
import streamlit as st
from psycopg import Connection
from config.settings import DB_URI

#DB_URI= "dbname= chatbot host=127.0.0.1 user=postgres password=4455 port=5432"

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0
}

#initialise the checkpointer
def create_checkpointer():
    conn = Connection.connect(DB_URI, **connection_kwargs)
    return conn