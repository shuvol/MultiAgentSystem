# 定义图
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.center_graph.state import CenterState
from src.environment_monitor_graph.prompt import environment_monitor_prompt
from src.graph_common.assistant import AgriAssistant

environment_monitor_builder = StateGraph(CenterState)
# 增加llm node
environment_monitor_builder.add_node("monitor_environment_ast", AgriAssistant(prompt=environment_monitor_prompt))

environment_monitor_builder.add_edge(START, "monitor_environment_ast")
environment_monitor_builder.add_edge("monitor_environment_ast", END)
