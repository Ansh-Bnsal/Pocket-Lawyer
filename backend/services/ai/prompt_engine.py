import json
from .prompts import chat, doc_analysis, analyze_case

class PromptEngine:
    TEMPLATES = {
        "chat": chat,
        "doc_analysis": doc_analysis,
        "analyze_case": analyze_case
    }

    @classmethod
    def build(cls, task: str, user_input: str, context: str = None) -> str:
        """
        Construct the final system-prompt + user-input string.
        """
        template = cls.TEMPLATES.get(task, chat) # Default to chat
        
        # 🧪 SYSTEM BLOCK
        full_prompt = template.SYSTEM_PROMPT
        
        # 🧪 SCHEMA BLOCK (Strict JSON enforcement)
        full_prompt += "\n\nCRITICAL: You MUST output ONLY valid JSON matching this schema:\n"
        full_prompt += json.dumps(template.OUTPUT_SCHEMA, indent=2)
        
        # 🧪 CONTEXT BLOCK
        if context:
            full_prompt += f"\n\nEXTRA CONTEXT:\n{context}"
            
        # 🧪 USER BLOCK
        full_prompt += f"\n\nUSER INPUT / PROBLEM DESCRIPTION:\n{user_input}"
        
        return full_prompt
