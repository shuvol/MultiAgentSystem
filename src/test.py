from pydantic import BaseModel, Field


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

    assistant: str = Field(default="monitor_environment_assistant", description="对应的assistant名字")

    class Config:
        json_schema_extra = {
            "示例": {
                "img_path": "agent/wwc/graph2.png",
                "request": "我想知道这个作物发生什么了,怎么防治?。",
            }
        }



print(ToDiseaseAndPestAssistant.model_fields["assistant"].default)