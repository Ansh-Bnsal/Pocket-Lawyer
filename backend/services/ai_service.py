"""
Pocket Lawyer 2.0 — AI Service (The Anti-Chatbot Engine)
Uses LLM APIs STRICTLY as a Data Extraction Engine.
No conversational pleasantries. Pure structured JSON output.

Supports: Google Gemini (default), OpenAI, Anthropic
Swap provider by setting AI_PROVIDER env var.
"""
import json
import requests
from config import (
    AI_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
)

# ── System Prompts ────────────────────────────────────────────────────────────

CASE_ANALYSIS_PROMPT = """You are a Legal Case Structuring Engine. You are NOT a chatbot. You do NOT make small talk. You do NOT say "thank you" or "I understand."

Your ONLY job: read the user's legal problem and output a structured JSON analysis.

You MUST output valid JSON with this exact schema:
{
  "caseClassification": "string — the legal category (e.g., Traffic Violation, Family Law, Property Dispute, Criminal Matter, Consumer Rights, Labor Dispute, etc.)",
  "applicableLaws": ["string — list of relevant laws, acts, or sections that apply"],
  "summary": "string — plain language explanation of what is happening, written so a non-lawyer can understand",
  "riskAssessment": {
    "level": "HIGH | MEDIUM | LOW",
    "explanation": "string — why this risk level, what could go wrong"
  },
  "riskHighlights": [
    {
      "severity": "HIGH | MEDIUM | LOW",
      "issue": "string — the specific risk or concern",
      "explanation": "string — why this matters and what could happen",
      "recommendation": "string — what the user should do about this"
    }
  ],
  "actionPlan": [
    {
      "step": 1,
      "action": "string — what to do",
      "reason": "string — why this step matters",
      "urgency": "IMMEDIATE | SOON | WHEN_READY"
    }
  ],
  "rightsAwareness": ["string — specific legal rights the person has in this situation"],
  "needsLawyer": true/false,
  "lawyerDomain": "string — if needsLawyer is true, what type of lawyer is needed"
}

Rules:
- Output ONLY the JSON. No markdown, no explanation, no preamble.
- Be specific to Indian law where applicable.
- If the input is vague, still output the best analysis you can.
- Always provide at least 3 action steps.
- Always provide at least 2 risk highlights."""

DOCUMENT_ANALYSIS_PROMPT = """You are a Legal Document Risk Analysis Engine. You are NOT a chatbot.

You will receive text extracted from a legal document (contract, notice, agreement, etc.).

Your job:
1. Explain the entire document in simple language
2. Identify every risky clause, phrase, or obligation
3. Mark each risk with severity (HIGH/MEDIUM/LOW)
4. Quote the EXACT phrase from the document that is risky
5. Suggest what a fair version of each risky clause would look like

Output valid JSON with this schema:
{
  "documentType": "string — what kind of document this is",
  "simplifiedExplanation": "string — the entire document explained in plain, simple language that a non-lawyer can understand",
  "overallRisk": "HIGH | MEDIUM | LOW",
  "riskHighlights": [
    {
      "severity": "HIGH | MEDIUM | LOW",
      "originalPhrase": "string — the EXACT text from the document",
      "explanation": "string — why this is risky in plain language",
      "consequence": "string — what can go wrong if you ignore this",
      "suggestedModification": "string — what a fair version would look like"
    }
  ],
  "obligations": ["string — things the signer is required to do"],
  "hiddenClauses": ["string — things that are easy to miss but important"],
  "openQuestions": ["string — ambiguous parts that should be clarified before signing"],
  "verdict": "string — overall recommendation: SAFE_TO_SIGN | PROCEED_WITH_CAUTION | DO_NOT_SIGN_WITHOUT_LAWYER"
}

Rules:
- Output ONLY the JSON. No markdown.
- Quote exact phrases from the document for risk highlights.
- Be thorough — check for penalties, auto-renewal, jurisdiction traps, one-sided clauses.
- Always provide at least 3 risk highlights if the document has any complexity."""

CHAT_RESPONSE_PROMPT = """You are a Legal Guidance Engine for Indian law. You are NOT a chatbot — but you DO provide helpful, structured responses.

When a user asks a legal question:
1. Identify the legal domain
2. Explain their rights clearly
3. Provide actionable next steps
4. Flag any risks or deadlines

Output valid JSON:
{
  "domain": "string — legal domain this question falls under",
  "answer": "string — clear, helpful answer in plain language",
  "legalRights": ["string — specific rights the person has"],
  "actionSteps": [
    {
      "step": 1,
      "action": "string",
      "reason": "string"
    }
  ],
  "warnings": ["string — important cautions or deadlines"],
  "needsLawyer": true/false,
  "confidence": "HIGH | MEDIUM | LOW"
}

Rules:
- Be specific. No generic advice like "consult a lawyer" without also giving concrete guidance.
- Reference specific Indian laws/acts when relevant.
- Output ONLY valid JSON."""


# ── Provider Implementations ──────────────────────────────────────────────────

def _call_gemini(system_prompt, user_input):
    """Call Google Gemini API."""
    if not GEMINI_API_KEY:
        return _demo_response(user_input)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser Input:\n{user_input}"}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    text = data['candidates'][0]['content']['parts'][0]['text']
    return json.loads(text)


def _call_openai(system_prompt, user_input):
    """Call OpenAI API."""
    if not OPENAI_API_KEY:
        return _demo_response(user_input)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return json.loads(resp.json()['choices'][0]['message']['content'])


def _call_anthropic(system_prompt, user_input):
    """Call Anthropic Claude API."""
    if not ANTHROPIC_API_KEY:
        return _demo_response(user_input)

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_input}]
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    text = resp.json()['content'][0]['text']
    # Claude may wrap JSON in markdown code blocks
    if text.startswith('```'):
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    return json.loads(text.strip())


def _demo_response(user_input):
    """Fallback when no API key is configured. Returns a properly structured demo response."""
    return {
        "caseClassification": "General Legal Query",
        "summary": f"Analysis of: {user_input[:200]}. This is a DEMO response — configure an AI API key (GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY) for real legal analysis.",
        "riskAssessment": {"level": "MEDIUM", "explanation": "Unable to assess without AI API. Configure an API key for real analysis."},
        "riskHighlights": [
            {"severity": "MEDIUM", "issue": "Demo mode active", "explanation": "No AI provider configured. Set GEMINI_API_KEY environment variable.", "recommendation": "Configure API key for production use."}
        ],
        "actionPlan": [
            {"step": 1, "action": "Configure AI API key", "reason": "Required for real legal analysis", "urgency": "IMMEDIATE"},
            {"step": 2, "action": "Retry your query", "reason": "AI will provide specific legal guidance", "urgency": "SOON"},
            {"step": 3, "action": "Consult a qualified lawyer", "reason": "For matters requiring professional judgment", "urgency": "WHEN_READY"}
        ],
        "rightsAwareness": ["This is demo mode. Real analysis requires an API key."],
        "needsLawyer": False,
        "lawyerDomain": None,
        "_demo": True
    }


# ── Dispatcher ────────────────────────────────────────────────────────────────

def _call_ai(system_prompt, user_input):
    """Route to the configured AI provider."""
    providers = {
        'gemini': _call_gemini,
        'openai': _call_openai,
        'anthropic': _call_anthropic,
    }
    provider_fn = providers.get(AI_PROVIDER, _call_gemini)
    return provider_fn(system_prompt, user_input)


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_case(description):
    """Analyze a legal problem and return structured Case Token data."""
    return _call_ai(CASE_ANALYSIS_PROMPT, description)


def analyze_document(extracted_text):
    """Analyze a legal document for risks and simplification."""
    return _call_ai(DOCUMENT_ANALYSIS_PROMPT, extracted_text)


def chat_response(message, case_context=None):
    """Generate structured legal guidance for a chat query."""
    full_input = message
    if case_context:
        full_input = f"Case Context:\n{case_context}\n\nUser Question:\n{message}"
    return _call_ai(CHAT_RESPONSE_PROMPT, full_input)


def generate_case_summary(description):
    """Generate a plain-text summary for a case (used by case creation)."""
    result = analyze_case(description)
    return result.get('summary', description[:200])
