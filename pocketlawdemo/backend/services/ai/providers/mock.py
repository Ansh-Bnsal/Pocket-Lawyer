"""
Pocket Lawyer 2.0 — Mock AI Provider
Provides high-quality, pre-defined legal responses for Demo Mode.
Used when no API key is configured.
"""
import json
import time

class MockProvider:
    def generate(self, prompt: str, file_data: dict = None, model: str = None) -> str:
        """
        Return a realistic 'The Anti-Chatbot' JSON response based on the task.
        """
        # Simulate 'Thinking' time for realism
        time.sleep(1.5)

        # 🧩 TASK DETECTION (Simple heuristic for mock responses)
        if "simplifiedExplanation" in prompt:
            # Task: Document Analysis
            return json.dumps({
                "document_type": "Rental Agreement (Demo)",
                "simplifiedExplanation": "This is a standard 11-month residential rent agreement. Most clauses are standard for India, but some termination and penalty clauses are biased.",
                "overallRisk": "MEDIUM",
                "harmfulClauses": [
                    {
                        "severity": "HIGH",
                        "originalQuote": "The Landlord may terminate this agreement at any time with 24 hours notice.",
                        "explanation": "Extremely short notice period. Standard is 30 days.",
                        "consequence": "User could be evicted with almost no warning.",
                        "suggestedFix": "Change to 30 days written notice for both parties."
                    },
                    {
                        "severity": "MEDIUM",
                        "originalQuote": "Interest on late rent shall be 18% per month.",
                        "explanation": "Extremely high interest rate.",
                        "consequence": "A small delay in rent could lead to heavy debt.",
                        "suggestedFix": "Reduce to 2% per month maximum."
                    }
                ],
                "obligations": ["Pay rent by 5th", "Pay electricity bills", "Maintain the property"],
                "verdict": "PROCEED_WITH_CAUTION"
            })

        elif "caseClassification" in prompt:
            # Task: Case Analysis
            return json.dumps({
                "summary": "The user is facing a security deposit dispute with their landlord. The landlord is refusing to refund the deposit despite the tenant vacating properly.",
                "caseClassification": "Property & Tenancy (Demo)",
                "riskLevel": "MEDIUM",
                "riskHighlights": [
                    {"severity": "MEDIUM", "issue": "Lack of written evidence", "explanation": "If no move-out inspection was done.", "recommendation": "Gather all receipts."}
                ],
                "actionPlan": [
                    {"step": 1, "action": "Send Legal Notice", "urgency": "IMMEDIATE"}
                ],
                "applicableLaws": ["Indian Contract Act", "State Rent Control Act"]
            })

        else:
            # Task: Chat
            return json.dumps({
                "answer": "I have analyzed your situation. Under Indian Law, specifically the Negotiable Instruments Act Section 138, a bounced cheque is a serious matter. You should immediately send a Demand Notice to the issuer within 30 days of the cheque bounce.",
                "legalRights": ["Right to demand payment", "Right to file criminal complaint"],
                "actionSteps": [
                    {"step": 1, "action": "Issue Section 138 Legal Notice", "reason": "Mandatory first step for recovery"}
                ],
                "warnings": ["Do not miss the 30-day notice deadline"],
                "domain": "Cheque Bounce / Financial Debt",
                "needsLawyer": True
            })
