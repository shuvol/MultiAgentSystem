from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from configuration import config_llm
from src.graph_common.state import State


class AgriAssistant:
    llm = config_llm

    def __init__(self, prompt: ChatPromptTemplate, tools=None, llm=config_llm):
        """
        初始化助手的实例。
        """
        self.tools = tools
        if tools is None:
            self.runnable = prompt | llm
        else:
            self.runnable = prompt | llm.bind_tools(tools)

    def __call__(self, state: State):
        """
        调用节点，执行助手任务
        :param state: 当前工作流的状态
        :param config: 配置: 里面有用户的信息
        :return:
        """
        while True:
            # 创建了一个无限循环，它将一直执行直到：从 self.runnable 获取的结果是有效的。
            # 如果结果无效（例如，没有工具调用且内容为空或内容不符合预期格式），循环将继续执行，
            # state = {**state, 'config': xxxxxx}  # 从配置中得到用户的信息，也追加到state，这里还没有接入，故先缺省
            result = self.runnable.invoke(state)
            # 如果，runnable执行完后，没有得到一个实际的输出
            if not result.tool_calls and (  # 如果结果中没有工具调用，并且内容为空或内容列表的第一个元素没有"text"，则需要重新提示用户输入。
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "请提供一个真实的输出作为回应。")]  # 给出一个隐式的用户输入
                state = {**state, "messages": messages}
            else:  # 如果： runnable执行后已经得到，想要的输出，则退出循环
                break
        return {'messages': result}
