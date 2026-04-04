from .prompt_engine import PromptEngine
from .normalizer import Normalizer, AIResult
from .providers.gemini import GeminiProvider
from .providers.mock import MockProvider
from config import AI_PROVIDER, GEMINI_CHAT_KEY, GEMINI_INTENT_KEY, GEMINI_RISK_KEY

class AIGateway:
    def __init__(self):
        # [Registry] PROVIDER REGISTRY
        self.providers = {
            "gemini": GeminiProvider(model_name="gemini-2.5-flash"),
            "mock": MockProvider(),
        }

    def ask(self, task: str, user_input: str, file_data: dict = None, context: str = None, history: list = None, api_key: str = None) -> AIResult:
        """
        Universal entry point. Returns AIResult(text, data).
        """
        try:
            # 1. [Prompt] BUILD PROMPT
            prompt = PromptEngine.build(task, user_input, context)
            
            # 2. [Select] SELECT PROVIDER
            provider_key = AI_PROVIDER.lower() if AI_PROVIDER else "gemini"
            k = api_key or GEMINI_CHAT_KEY
            is_demo = not k or "SyAja7GM0rwE" in k or len(k) < 20
            
            if is_demo:
                provider = self.providers["mock"]
            else:
                provider = self.providers.get(provider_key, self.providers["gemini"])
            
            # 3. [Call] CALL AI
            raw_response = provider.generate(prompt, file_data, history=history, api_key=api_key)
            
            # 4. [Clean] NORMALIZE
            result = Normalizer.clean(task, raw_response)
            
            if is_demo:
                result.text = "[Demo Mode - AI Mocking active]\n\n" + result.text
            
            return result
            
        except Exception as e:
            return AIResult(
                text=f"I'm sorry, I encountered a technical issue: {str(e)}.",
                data={"error": str(e)}
            )

    def ask_stream(self, task: str, user_input: str, file_data: dict = None, context: str = None, history: list = None, api_key: str = None):
        """
        Streaming entry point.
        """
        try:
            prompt = PromptEngine.build(task, user_input, context, is_streaming=True)
            
            provider_key = AI_PROVIDER.lower() if AI_PROVIDER else "gemini"
            k = api_key or GEMINI_CHAT_KEY
            is_demo = not k or "SyAja7GM0rwE" in k or len(k) < 20
            
            if is_demo:
                provider = self.providers["mock"]
            else:
                provider = self.providers.get(provider_key, self.providers["gemini"])

            for chunk in provider.stream_generate(prompt, file_data, history=history, api_key=api_key):
                yield chunk

        except Exception as e:
            # 🏛️ Standardized Opaque Error Propagation
            print(f"[AI Gateway Failure] {str(e)}")
            raise e

# Export a singleton instance for global use
ai = AIGateway()
