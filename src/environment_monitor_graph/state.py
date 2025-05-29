"""环境监测智能体 State"""

from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from src.graph_common.state import State


class EnvironmentMonitorState(State):
    """
    环境监测智能体 State结构
    """

