import asyncio
import os
import uuid

from langgraph.checkpoint.memory import MemorySaver

from src.center_graph.graph import center_builder


_printed = set()  # set集合，避免重复打印
def _print_event(event: dict, _printed: set, max_length=1500):
    """
    打印事件信息，特别是对话状态和消息内容。如果消息内容过长，会进行截断处理以保证输出的可读性。

    参数:
        event (dict): 事件字典，包含对话状态和消息。
        _printed (set): 已打印消息的集合，用于避免重复打印。
        max_length (int): 消息的最大长度，超过此长度将被截断。默认值为1500。
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("当前处于: ", current_state[-1])  # 输出当前的对话状态
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]  # 如果消息是列表，则取最后一个
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... （已截断）"  # 超过最大长度则截断
            print(msg_repr)  # 输出消息的表示形式
            _printed.add(message.id)  # 将消息ID添加到已打印集合中

async def main():
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = "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"
    os.environ["LANGCHAIN_PROJECT"] = "multiAgentSystem"

    # 生成随机的唯一会话id
    session_id = str(uuid.uuid4())
    config = {
        "configurable": {
            # passenger_id用于我们的航班工具，以获取用户的航班信息
            "user_id": "3442 587242",
            # 检查点由session_id访问
            "thread_id": session_id,
        }
    }

    # 实例化一个用于保存/恢复内存状态的对象
    memory = MemorySaver()
    graph = center_builder.compile(checkpointer=memory)
    # 执行工作流
    while True:
        question = input('用户：')
        # 退出逻辑，目前只是样本，当用户输入的单词包括 q/exit/quit 时退出，也没有进行中译英
        if question.lower() in ['q', 'exit', 'quit']:
            print('对话结束，拜拜！')
            break
        else:
            # # 参数：input——对state的初始化更新，config——之前动态定义的配置字典，stream_mode——返回值（events）的格式
            # events = graph.stream({'messages': ('user', question)}, config, stream_mode='values')
            # # 打印消息，直到中断发生（或者用户退出退出）——builder.compile中定义了，当涉及到敏感工具时就会中断
            # for event in events:
            #     _print_event(event, _printed)
            # 使用 astream 异步流式处理事件
            async for event in graph.astream({'messages': ('user', question)}, config, stream_mode='values'):
                _print_event(event, _printed)


if __name__ == "__main__":
    asyncio.run(main())
