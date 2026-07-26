from typing import List
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from src.llm.provider import LLMProvider
import os

class LlamaSwapProvider(LLMProvider):
    def __init__(self, model: str, base_url: str = None):
        self.model = model
        self.base_url = base_url
        # llama-swap is usually accessed via an OpenAI-compatible endpoint
        # or a custom inference server. We assume an OpenAI-compatible 
        # endpoint for consistency with the existing LangChain infrastructure.
        from langchain_openai import ChatOpenAI
        self.chat_model = ChatOpenAI(
            model=model,
            openai_api_base=base_url,
            openai_api_key="not-needed"  # llama-swap doesn't require a key
        )

    def generate_response(self, messages: List[BaseMessage]) -> BaseMessage:
        return self.chat_model.invoke(messages)

    def bind_tools(self, tools: List[Runnable]) -> Runnable:
        return self.chat_model.bind_tools(tools)
