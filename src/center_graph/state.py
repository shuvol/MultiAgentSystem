"""中央智能体 State"""

from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from src.graph_common.state import State


class CenterState(State):
    """
    中央智能体 State结构
    """

