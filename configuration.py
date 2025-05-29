import os

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

config_llm = ChatOpenAI(
    base_url=os.environ.get('LLM_BASE_URL', ''),
    api_key=os.environ.get('LLM_API_KEY', ''),
    model_name=os.environ.get('LLM_MODEL_NAME', ''),
    # model_name="qwq-plus",
    temperature=0,
    # streaming=True,
)
