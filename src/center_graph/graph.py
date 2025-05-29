from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from src.center_graph.prompt import primary_assistant_prompt
from src.center_graph.state import CenterState
from src.disease_pest_graph.graph import disease_pest_builder
from src.environment_monitor_graph.graph import environment_monitor_builder
from src.graph_common.assistant import AgriAssistant

# 用于主图感知子图的方法
class ToEnvironmentMonitorAssistant(BaseModel):
    """
    咨询环境数据采集与分析的环境监测助理。
    """

    request: str = Field(
        description="用户想要了解的环境的地点"
    )

    assistant: str = Field(default="monitor_environment_assistant", description="对应的assistant名字")

class ToDiseaseAndPestAssistant(BaseModel):
    """
    咨询专门处理病虫害管理的助理。
    """
    img_path: str = Field(
        description="图像存储的地址"
    )

    request: str = Field(
        description="用户想要了解的病害或虫害的种类以及防治办法"
    )

    assistant: str = Field(default="disease_pest_assistant", description="对应的assistant名字")

    class Config:
        json_schema_extra = {
            "示例": {
                "img_path": "agent/wwc/graph2.png",
                "request": "我想知道这个作物发生什么了,怎么防治?。",
            }
        }

tools = [ToEnvironmentMonitorAssistant, ToDiseaseAndPestAssistant]


# 路由规则
tools_by_name = {tool.__name__: tool for tool in tools}
def route(state: CenterState):
    if messages := state.get("messages", []):
        message = messages[-1]
    else:
        raise ValueError("No message found in input")
    outputs = []
    for tool_call in message.tool_calls:
        assistant_node = tools_by_name[tool_call["name"]].model_fields["assistant"].default
        outputs.append(assistant_node)

    #outputs = ["disease_pest_assistant", "monitor_environment_assistant"]
    return outputs


disease_pest_graph = disease_pest_builder.compile()
environment_monitor_graph = environment_monitor_builder.compile()

async def consult_disease_pest_assistant(state: CenterState):
    # 多重工具调用下获取工具调用ID
    tool_call_id = None
    tool_request = None
    for tool_call in state["messages"][-1].tool_calls:
        if tool_call["name"] == ToDiseaseAndPestAssistant.__name__:
            tool_call_id = tool_call["id"]
            tool_request = tool_call["args"]["request"]

    assistant_input_format = {"messages": [{"role": "system", "content": tool_request}]}
    result = await disease_pest_graph.ainvoke(assistant_input_format)

    return  {
            "messages": [
                ToolMessage(
                    content=f"助手'disease_pest_assistant'返回消息:{result['messages'][-1].content}",
                    tool_call_id=tool_call_id,
                )
            ]
        }

async def consult_monitor_environment_assistant(state: CenterState):
    # 多重工具调用下获取工具调用ID和调用参数
    tool_call_id = None
    tool_request = None
    for tool_call in state["messages"][-1].tool_calls:
        if tool_call["name"] == ToEnvironmentMonitorAssistant.__name__:
            tool_call_id = tool_call["id"]
            tool_request = tool_call["args"]["request"]

    assistant_input_format = {"messages": [{"role": "system", "content": tool_request}]}
    result = await environment_monitor_graph.ainvoke(assistant_input_format)

    return  {
            "messages": [
                ToolMessage(
                    content=f"助手'monitor_environment_assistant'返回消息:{result['messages'][-1].content}",
                    tool_call_id=tool_call_id,
                )
            ]
        }


# 定义图
center_builder = StateGraph(CenterState)
# 增加llm node
center_builder.add_node("primary_assistant", AgriAssistant(prompt=primary_assistant_prompt, tools=tools))
# 增加子图 node
center_builder.add_node("disease_pest_assistant", consult_disease_pest_assistant)
center_builder.add_node("monitor_environment_assistant", consult_monitor_environment_assistant)

center_builder.add_edge(START, "primary_assistant")
center_builder.add_conditional_edges("primary_assistant", route, ["disease_pest_assistant", "monitor_environment_assistant", END])
center_builder.add_edge("disease_pest_assistant", "primary_assistant")
center_builder.add_edge("monitor_environment_assistant", "primary_assistant")

