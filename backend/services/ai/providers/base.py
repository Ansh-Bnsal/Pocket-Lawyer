"""
Pocket Lawyer 2.0 — Base AI Provider
Abstract interface for all AI models. Any new provider (Gemini, OpenAI, Custom) 
must implement the `generate` method.
"""
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, file_data: dict = None, model: str = None) -> str:
        """
        Send a fully constructed prompt to the AI provider.
        
        Args:
            prompt: The full string (including system instructions).
            file_data: Optional { "mime_type": "...", "base64": "..." }.
            model: Optional model override (e.g., "gemini-1.5-flash").
            
        Returns:
            The raw string response from the provider.
        """
        pass
