"""
Pocket Lawyer 2.0 — Base AI Provider
Abstract interface for all AI models. Any new provider (Gemini, OpenAI, Custom) 
must implement the `generate` method.
"""
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, file_data: dict = None, history: list = None, api_key: str = None) -> str:
        """
        Send a fully constructed prompt to the AI provider.
        """
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, file_data: dict = None, history: list = None, api_key: str = None):
        """
        Stream text chunks from the AI provider.
        """
        pass
