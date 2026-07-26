from abc import ABC, abstractmethod
from typing import List
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
import os

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, messages: List[BaseMessage]) -> BaseMessage:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def bind_tools(self, tools: List[Runnable]) -> Runnable:
        """Bind tools to the LLM model."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize ChatOpenAI
        self.chat_model = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url
        )

    def generate_response(self, messages: List[BaseMessage]) -> BaseMessage:
        return self.chat_model.invoke(messages)

    def bind_tools(self, tools: List[Runnable]) -> Runnable:
        return self.chat_model.bind_tools(tools)
