# Pocket Lawyer 2.0 ⚖️
**An AI-Native Legal Case Management & Documentation Platform**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange?logo=google-gemini)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Pocket Lawyer 2.0 is a full-stack SaaS platform designed to solve the **"Fragmented Legal Data"** problem. It uses a revolutionary **"Case → Structure → Store → Continue"** paradigm to ensure that legal history is never lost, even if lawyers change.

---

## 🛠️ Engineering Highlights (Core Technical Architecture)

This project isn't just a chatbot; it's a **Legal Information Engine**. Behind the UI, I've implemented several advanced patterns to solve common LLM challenges:

### 🧠 1. Rolling Summary Memory (Context Optimization)
To solve the "Context Leak" problem in long legal conversations, I developed a **Rolling Summary Engine**. 
*   **The Tech**: The backend monitors message count. For every 19 messages, it triggers an asynchronous summarization of the history and compresses it into a "State Token," which is then securely prepended to the next prompt.
*   **Result**: Infinite conversational memory with zero token bloat.

### 🛡️ 2. Global Rate-Limit Shield (Scalability)
Free-tier AI APIs (like Gemini) are prone to `429 Too Many Requests` errors.
*   **The Tech**: Implemented a global `threading.Lock()` and a **Production-Grade Request Queue** in the AIOrchestrator to prevent concurrent AI collisions.
*   **Result**: A stable UI experience that gracefully handles traffic bursts.

### 🔌 3. Double-Proxy Architecture (API Flexibility)
Built on a **Decoupled Service Pattern**, the platform features a "LegalDesk Proxy."
*   **The Tech**: All calls to eSign (Aadhaar), eStamp (DigiStamp), and KYC (Video) are routed through a replaceable bridge. 
*   **Result**: The site works out-of-the-box with high-fidelity mock data, but can be switched to real Production API endpoints (SignDesk/Melento) just by swapping a single config file.

---

## 📋 Status & The "Full Vision" Roadmap

In adherence to community standards, this roadmap clearly distinguishes between **Functional Code** and the **Product Vision**.

### **Phase 1: Intelligence Core [COMPLETED]**
- [x] **Strict JSON Extraction Protocol**: AI returns only structured JSON for data integrity.
- [x] **12-Service Legal Catalog**: Full alignment with LegalDesk data requirements (Tenure, Escallation, Deposit).
- [x] **Ghost-Promotion Engine**: Conversational intent extraction to auto-save official cases.

### **Phase 2: Digital Vault [PLANNED]**
- [ ] **Vault UI**: Category-based secure storage (Drafts, Official, Identity).
- [ ] **Document Metadata Tracking**: Database-level state management for signed vs. pending docs.

### **Phase 3: Firm-Side Ecosystem [PLANNED]**
- [ ] **RAG Lawyer Research**: Retrieval-Augmented Generation for actual Indian Case Law (Precedents).
- [ ] **Firm Assignment Workflow**: Multi-lawyer case routing and tracking.

---

## 📂 Project Anatomy

```text
├── backend/
│   ├── services/
│   │   ├── ai_service.py       # Strict JSON-only prompt engine
│   │   ├── legal_desk_main.py  # Orchestrator for drafting/signing
│   │   └── legal_desk_proxy.py # The Production-Grade API Bridge
│   ├── database.py             # SQLite Schema with Automated Migration logic
│   └── app.py                  # Stream-enabled Flask Entry Point
└── frontend/
    ├── js/
    │   ├── services_shared.js  # Centralized Service Mapping & AI pre-filling
    │   └── api.js              # Tokenized JWT networking layer
    └── dashboard.html          # High-fidelity Case Management UI
```

---

## 🚀 Speed-Dating the Demo (HR Quick Start)

1.  **Clone & Install**: `cd backend && pip install -r requirements.txt`
2.  **API Key**: Add your `GEMINI_API_KEY` to `.env` (Google AI Studio keys work instantly).
3.  **Run**: `python app.py`
4.  **The "Wow" Moment**: Open the Chat, say *"I need a residential rent agreement for 11 months with a 15k deposit"* — watch the AI extract the data and pre-fill the complex legal form instantly.

---

## ⚖️ License
MIT License - Developed by Ansh Bansal.
