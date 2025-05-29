"""基础State"""
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class State(TypedDict):
    """
    基础State结构，各个智能体都共同拥有的属性
    """
    messages: Annotated[list[AnyMessage], add_messages]