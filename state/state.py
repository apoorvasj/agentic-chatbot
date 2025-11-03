from typing_extensions import TypedDict
from typing import Annotated
from typing import List, Tuple
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class State(TypedDict):
    """
    Represents the structure of the state used in the graph.
    """
    question : str = ""
    documents: List[str] = ["docs"]
    generation: str = ""
    re_gen_required: str = ""
    re_gen_limit: int = 0
    hallucination_present: str = ""