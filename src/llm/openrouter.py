from typing import List
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
import os

class OpenRouterProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        
        # OpenRouter is OpenAI-compatible
        self.chat_model = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            default_headers={"HTTP-Referer": os.getenv("SITE_URL"), "X-Title": "SensusVault"}
        )

    def generate_response(self, messages: List[BaseMessage]) -> BaseMessage:
        return self.chat_model.invoke(messages)

    def bind_tools(self, tools: List[Runnable]) -> Runnable:
        return self.chat_model.bind_tools(tools)
