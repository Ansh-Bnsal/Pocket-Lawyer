"""
Pocket Lawyer 2.0 — Output Normalizer
Translates complex AI JSON into "Clean Text" and Structured Data.
"""
import json

class AIResult:
    """
    Standard object returned by the AI Gateway to the main app.
    Prevents the main app from having to parse JSON or know AI keys.
    """
    def __init__(self, text: str, data: dict = None):
        self.text = text
        self.data = data or {}

    def __getitem__(self, key):
        return self.data.get(key)
    
    def get(self, key, default=None):
        return self.data.get(key, default)

class Normalizer:
    @classmethod
    def clean(cls, task: str, raw_response: str) -> AIResult:
        """
        Main entry point for normalization.
        Returns an AIResult object.
        """
        try:
            # Extract JSON
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("```")[1]
                if clean_json.startswith("json"):
                    clean_json = clean_json[4:]
            
            data = json.loads(clean_json)
            
            # Format human-readable text
            if task == "chat":
                text = cls._format_chat(data)
            elif task == "doc_analysis":
                text = cls._format_doc_analysis(data)
            elif task == "analyze_case":
                text = data.get('summary', '')
            else:
                text = str(data)

            return AIResult(text=text, data=data)
            
        except Exception as e:
            # Fallback for non-JSON or failed parse
            return AIResult(text=raw_response, data={"error": str(e)})

    @staticmethod
    def _format_chat(data):
        text = data.get('answer', '')
        rights = data.get('legalRights', [])
        if rights:
            text += "\n\n📋 **YOUR LEGAL RIGHTS**\n" + "\n".join(f"• {r}" for r in rights)
        steps = data.get('actionSteps', [])
        if steps:
            text += "\n\n🎯 **ACTION PLAN**\n"
            for s in steps:
                text += f"{s.get('step', '')}. **{s.get('action', '')}** — {s.get('reason', '')}\n"
        warnings = data.get('warnings', [])
        if warnings:
            text += "\n\n⚠️ **URGENT WARNINGS**\n" + "\n".join(f"• {w}" for w in warnings)
        return text

    @staticmethod
    def _format_doc_analysis(data):
        text = f"### {data.get('documentType', 'Document Analysis').upper()}\n\n"
        text += f"**Verdict:** {data.get('verdict', 'Needs Lawyer Review')}\n"
        text += f"**Risk Level:** {data.get('overallRisk', 'MEDIUM')}\n\n"
        text += f"**Simplified Summary:** {data.get('simplifiedExplanation', '')}\n\n"
        clauses = data.get('harmfulClauses', [])
        if clauses:
            text += "🚩 **HARMFUL CLAUSES DETECTED**\n"
            for c in clauses:
                text += f"\n- **[{c.get('severity', 'HIGH')}]** *\"{c.get('originalQuote', '')}\"*\n"
                text += f"  **Risk:** {c.get('explanation', '')}\n"
                text += f"  **Consequence:** {c.get('consequence', '')}\n"
                text += f"  **Suggested Fix:** {c.get('suggestedFix', '')}\n"
        return text
