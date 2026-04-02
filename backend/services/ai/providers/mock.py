import json
from .base import BaseProvider

class MockProvider(BaseProvider):
    def generate(self, prompt: str, file_data: dict = None, model: str = None) -> str:
        if "simplifiedExplanation" in prompt:
            return json.dumps({
                "document_type": "Rental Agreement (Demo)",
                "simplifiedExplanation": "This is a standard 11-month residential rent agreement.",
                "overallRisk": "MEDIUM",
                "harmfulClauses": [],
                "missingClauses": []
            })

        if "caseType" in prompt:
            return json.dumps({
                "caseType": "Property & Real Estate",
                "riskLevel": "high",
                "extractedEntities": {},
                "summary": "Mock summary",
                "initialAdvice": ["Gather documents"],
                "recommendedActions": ["Draft notice"]
            })

        return json.dumps({
            "answer": "This is a mocked API response. Please configure GEMINI_API_KEY for real analysis.",
            "followUp": "Do you have any more details?",
            "action": "none"
        })

    def stream_generate(self, prompt: str, file_data: dict = None, model: str = None):
        import time
        chunks = ["This ", "is ", "a ", "mocked ", "streaming ", "response ", "because ", "you ", "are ", "in ", "demo ", "mode."]
        for chunk in chunks:
            time.sleep(0.1)
            yield chunk
