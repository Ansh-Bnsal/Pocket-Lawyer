from .prompt_engine import PromptEngine
from .normalizer import Normalizer, AIResult
from .providers.gemini import GeminiProvider
from .providers.mock import MockProvider
from config import AI_PROVIDER, GEMINI_API_KEY

class AIGateway:
    def __init__(self):
        # 🔌 PROVIDER REGISTRY
        self.providers = {
            "gemini": GeminiProvider(),
            "mock": MockProvider(),
        }

    def ask(self, task: str, user_input: str, file_data: dict = None, context: str = None) -> AIResult:
        """
        Universal entry point. Returns AIResult(text, data).
        Automatically switches to MockProvider if API Key is missing.
        """
        try:
            # 1. 📜 BUILD PROMPT
            prompt = PromptEngine.build(task, user_input, context)
            
            # 2. 🔌 SELECT PROVIDER (With Demo Check)
            provider_key = AI_PROVIDER.lower() if AI_PROVIDER else "gemini"
            is_demo = not GEMINI_API_KEY
            
            if is_demo:
                provider = self.providers["mock"]
            else:
                provider = self.providers.get(provider_key, self.providers["gemini"])
            
            # 3. 🚀 CALL AI
            raw_response = provider.generate(prompt, file_data)
            
            # 4. 🧹 NORMALIZE
            result = Normalizer.clean(task, raw_response)
            
            # 5. 🏷️ ADD DEMO TAG
            if is_demo:
                result.text = "[Demo Mode — AI Mocking active]\n\n" + result.text
            
            return result
            
        except Exception as e:
            # SAFETY FALLBACK: Professional error context
            return AIResult(
                text=f"I'm sorry, I encountered a technical issue while analyzing your request: {str(e)}.",
                data={"error": str(e)}
            )

# Export a singleton instance for global use
ai = AIGateway()
