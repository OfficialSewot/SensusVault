import os
from typing import Optional, Any
from src.llm.provider import LLMProvider
from src.llm.openrouter import OpenRouterProvider
from src.llm.anthropic import AnthropicProvider
from src.llm.local import LlamaSwapProvider
from src.llm.provider import OpenAIProvider
from langchain_openai import ChatOpenAI

class LLMFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if provider_type == "openai":
            return OpenAIProvider(
                model=os.getenv("LLM_MODEL", "gpt-4o"),
                api_key=os.getenv("LLM_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL")
            )
        elif provider_type == "openrouter":
            return OpenRouterProvider(
                model=os.getenv("LLM_MODEL", "meta-llama/llama-3-70b-instruct"),
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            )
        elif provider_type == "anthropic":
            return AnthropicProvider(
                model=os.getenv("LLM_MODEL", "claude-3-5-sonnet-20240620"),
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif provider_type == "llama_swap":
            return LlamaSwapProvider(
                model=os.getenv("LLM_MODEL", "gemma4-12b"),
                base_url=os.getenv("LLAMA_SERVER_URL")
            )
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {provider_type}")

    @staticmethod
    def get_runnable() -> Any:
        provider = LLMFactory.get_provider()
        # We will call bind_tools on the provider's underlying model
        # Note: This requires the agent to pass tools to the factory
        return provider
