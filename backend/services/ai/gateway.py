from .prompt_engine import PromptEngine
from .normalizer import Normalizer, AIResult
from .providers.gemini import GeminiProvider
from .providers.mock import MockProvider
from config import AI_PROVIDER, GEMINI_API_KEY

class AIGateway:
    def __init__(self):
        # [Registry] PROVIDER REGISTRY
        self.providers = {
            "gemini": GeminiProvider(model_name="gemini-flash-latest"),
            "mock": MockProvider(),
        }

    def ask(self, task: str, user_input: str, file_data: dict = None, context: str = None) -> AIResult:
        """
        Universal entry point. Returns AIResult(text, data).
        Automatically switches to MockProvider if API Key is missing.
        """
        try:
            # 1. [Prompt] BUILD PROMPT
            prompt = PromptEngine.build(task, user_input, context)
            
            # 2. [Select] SELECT PROVIDER (With Demo Check)
            provider_key = AI_PROVIDER.lower() if AI_PROVIDER else "gemini"
            # Detect placeholder vs real key (Match config.py placeholder)
            is_demo = not GEMINI_API_KEY or "SyAja7GM0rwE" in GEMINI_API_KEY or len(GEMINI_API_KEY) < 20
            
            if is_demo:
                provider = self.providers["mock"]
            else:
                provider = self.providers.get(provider_key, self.providers["gemini"])
            
            # 3. [Call] CALL AI
            raw_response = provider.generate(prompt, file_data)
            
            # 4. [Clean] NORMALIZE
            result = Normalizer.clean(task, raw_response)
            
            # 5. [Tag] ADD DEMO TAG
            if is_demo:
                result.text = "[Demo Mode - AI Mocking active]\n\n" + result.text
            
            return result
            
        except Exception as e:
            # SAFETY FALLBACK: Professional error context
            return AIResult(
                text=f"I'm sorry, I encountered a technical issue while analyzing your request: {str(e)}.",
                data={"error": str(e)}
            )

    def ask_stream(self, task: str, user_input: str, file_data: dict = None, context: str = None):
        """
        Streaming entry point for realtime typing effect. Bypasses Normalizer.
        """
        try:
            prompt = PromptEngine.build(task, user_input, context, is_streaming=True)
            
            provider_key = AI_PROVIDER.lower() if AI_PROVIDER else "gemini"
            # Detect placeholder vs real key (Match config.py placeholder)
            is_demo = not GEMINI_API_KEY or "SyAja7GM0rwE" in GEMINI_API_KEY or len(GEMINI_API_KEY) < 20
            
            if is_demo:
                provider = self.providers["mock"]
            else:
                provider = self.providers.get(provider_key, self.providers["gemini"])

            for chunk in provider.stream_generate(prompt, file_data):
                yield chunk

        except Exception as e:
            yield f"\n\n[Connection Error: {str(e)}]"

# Export a singleton instance for global use
ai = AIGateway()
