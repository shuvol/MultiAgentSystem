from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.center_graph.state import CenterState
from src.disease_pest_graph.prompt import disease_pest_prompt
from src.graph_common.assistant import AgriAssistant




# 定义图
disease_pest_builder = StateGraph(CenterState)
# 增加llm node
disease_pest_builder.add_node("disease_pest_ast", AgriAssistant(prompt=disease_pest_prompt))

disease_pest_builder.add_edge(START, "disease_pest_ast")
disease_pest_builder.add_edge("disease_pest_ast", END)


