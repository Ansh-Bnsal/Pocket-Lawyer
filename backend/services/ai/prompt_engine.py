import json
from .prompts import chat, chat_doc, doc_analysis, analyze_case

class PromptEngine:
    TEMPLATES = {
        "chat": chat,
        "chat_doc": chat_doc,
        "doc_analysis": doc_analysis,
        "analyze_case": analyze_case
    }

    @classmethod
    def build(cls, task: str, user_input: str, context: str = None, is_streaming: bool = False) -> str:
        """
        Construct the final system-prompt + user-input string.
        """
        template = cls.TEMPLATES.get(task, chat) # Default to chat
        
        # 🧪 SYSTEM BLOCK
        full_prompt = template.SYSTEM_PROMPT
        
        # 🧪 SCHEMA BLOCK / STREAM FORMAT
        if is_streaming:
            full_prompt += "\n\nCRITICAL: Output your response as standard, highly-readable conversational Markdown text. DO NOT use JSON formatting.\n"
        else:
            full_prompt += "\n\nCRITICAL: You MUST output ONLY valid JSON matching this schema:\n"
            full_prompt += json.dumps(template.OUTPUT_SCHEMA, indent=2)
        
        # 🧪 CONTEXT BLOCK
        if context:
            full_prompt += f"\n\nEXTRA CONTEXT:\n{context}"
            
        # 🧪 USER BLOCK
        full_prompt += f"\n\nUSER INPUT / PROBLEM DESCRIPTION:\n{user_input}"
        
        return full_prompt
