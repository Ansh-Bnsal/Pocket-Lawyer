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
            text += "\n\n[YOUR LEGAL RIGHTS]\n" + "\n".join(f"  {r}" for r in rights)
        steps = data.get('actionSteps', [])
        if steps:
            text += "\n\n[ACTION PLAN]\n"
            for s in steps:
                text += f"{s.get('step', '')}. **{s.get('action', '')}** — {s.get('reason', '')}\n"
        warnings = data.get('warnings', [])
        if warnings:
            text += "\n\n[URGENT WARNINGS]\n" + "\n".join(f"  {w}" for w in warnings)
        return text

    @staticmethod
    def _format_doc_analysis(data):
        severity_icons = {"HIGH": "[HIGH]", "MEDIUM": "[MEDIUM]", "LOW": "[LOW]"}
        
        # 1. SIMPLIFIED EXPLANATION
        text = f"[SIMPLIFIED EXPLANATION]:\n{data.get('simplifiedExplanation', '')}\n\n"
        
        # 2. USER RIGHTS (with Sections)
        rights = data.get('userRights', [])
        if rights:
            text += "[YOUR RIGHTS]:\n"
            for r in rights:
                text += f"• **{r.get('section', '')}:** {r.get('right', '')}\n"
            text += "\n"
        
        # 3. CATEGORY
        category = data.get('category', '')
        if category:
            text += f"[CATEGORY]: {category}\n\n"
        
        # 4. HARMFUL CLAUSES (3-Tier Severity)
        clauses = data.get('harmfulClauses', [])
        if clauses:
            text += f"[RISKS DETECTED IN CLAUSES]:\n"
            for c in clauses:
                sev = c.get('severity', 'MEDIUM').upper()
                icon = severity_icons.get(sev, "[MEDIUM]")
                clause_num = c.get('clauseNumber', '')
                simplification = c.get('simplification', c.get('explanation', ''))
                text += f"{icon} **{sev} Risk:** {clause_num} ({simplification})\n"
            
            text += "\n"
            # Detailed breakdown
            for c in clauses:
                sev = c.get('severity', 'MEDIUM').upper()
                icon = severity_icons.get(sev, "[MEDIUM]")
                text += f"\n{icon} **[{sev}] {c.get('clauseNumber', '')}**\n"
                text += f"  *\"{c.get('originalQuote', '')}\"*\n"
                text += f"  **Simplification:** {c.get('simplification', '')}\n"
                text += f"  **Risk:** {c.get('explanation', '')}\n"
                text += f"  **Consequence:** {c.get('consequence', '')}\n"
                text += f"  **Suggested Fix:** {c.get('suggestedFix', '')}\n"
        
        # 5. NEXT STEPS
        next_steps = data.get('nextSteps', '')
        if next_steps:
            text += f"\n**NEXT STEPS:**\n{next_steps}\n"
        
        # 6. VERDICT
        verdict = data.get('verdict', '')
        risk = data.get('overallRisk', '')
        if verdict:
            verdict_icon = {"SAFE_TO_SIGN": "[SAFE]", "PROCEED_WITH_CAUTION": "[CAUTION]", "DO_NOT_SIGN": "[WARNING]"}.get(verdict, "[CHECK]")
            text += f"\n{verdict_icon} **VERDICT:** {verdict.replace('_', ' ')} (Overall Risk: {risk})\n"
        
        return text
