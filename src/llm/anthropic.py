from typing import List
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_anthropic import ChatAnthropic
from src.llm.provider import LLMProvider

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        
        # Initialize ChatAnthropic
        self.chat_model = ChatAnthropic(
            model=model,
            anthropic_api_key=api_key
        )

    def generate_response(self, messages: List[BaseMessage]) -> BaseMessage:
        return self.chat_model.invoke(messages)

    def bind_tools(self, tools: List[Runnable]) -> Runnable:
        return self.chat_model.bind_tools(tools)
