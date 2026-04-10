# Pocket Lawyer 2.0 ⚖️

Pocket Lawyer 2.0 is a full-stack, AI-powered Legal SaaS platform. It acts as a smart, persistent case management system for Clients, Lawyers, and Law Firms. 

Unlike traditional platforms, this uses a revolutionary **"Case → Structure → Store → Continue"** paradigm powered by AI (Google Gemini / OpenAI / Anthropic) to extract structured legal Case Tokens from plain-text user input and document uploads.

---

## 🎯 Features

- **Ghost-Promotion Engine:** Start a casual text-based case prep. If the AI detects a legal injury or severe grievance (e.g. harassment, fraud), it transparently "Ghost-Promotes" the transient text into an official protected Case ID without user friction.
- **Smart Services Cart:** AI Intent Extractors automatically identify when a lawyer consultation or legal drafting is required and injects high-converting UI action cards directly into the sidebar stream.
- **Anti-Chatbot AI Engine:** Uses strict system prompts to force AI (Gemini/OpenAI) to return structured JSON data for case analysis, risk detection, and legal guidance instead of generic chatty responses.
- **Case Token System:** Case data is serialized into versioned JSON tokens. When a client switches lawyers, the new lawyer receives the complete, structured context instantly.
- **Document AI Processing:** Upload PDF/DOCX files and the AI automatically extracts the text, summarizes it, and highlights legal risks (RED/YELLOW/GREEN).
- **Role-Based Access:** Distinct secured dashboards for Clients, Lawyers, and Firm Administrators.
- **Zero-Config Database:** Uses SQLite to store cases, chat logs, notes, timelines, and documents. No need to run Postgres.

---

## 🛠️ Tech Stack

- **Frontend:** Vanilla HTML5, CSS3, JavaScript (No heavy frameworks)
- **Backend:** Python 3.10+ / Flask
- **Database:** SQLite (local persistent database)
- **AI Integrations:** Google Gemini / OpenAI / Anthropic
- **Security:** JWT-based Authentication + Password Hashing

---

## 🚀 How to Run Locally

### 1. Prerequisites
- [Python 3.10+](https://www.python.org/downloads/) installed.

### 2. Installation
Clone the repository, then navigate to the backend directory and install the required dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 3. API Key Configuration (Crucial)
To enable the AI structuring features, you **must** configure an API key. By default, the system uses Google Gemini's free tier. 

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API Key.
2. In the `backend` folder, duplicate the file named `.env.example`.
3. Rename the duplicated file to exactly `.env`.
4. Open your new `.env` file and paste your key:
   ```env
   # Google Gemini (default)
   GEMINI_API_KEY="PASTE_YOUR_KEY_HERE"
   ```
*(Note: `.env` is safely ignored by Git so your keys won't leak when you push!)*

### 4. Start the Application
```bash
python app.py
```
*The Flask server will automatically initialize the `pocket_lawyer.db` SQLite database.*

Navigate to **http://localhost:5000** in your browser.

---

## 📂 Project Structure

```
pocket-lawyer-2.0/
├── backend/
│   ├── app.py                  # Flask Entry Point
│   ├── config.py               # AI Provider & JWT Configurations
│   ├── database.py             # SQLite Connection & Schema setup
│   ├── requirements.txt        # Python Packages
│   ├── routes/                 # API Endpoints (Auth, Cases, Chat, Upload)
│   ├── services/
│   │   ├── ai_service.py       # Strict AI-prompt engine
│   │   └── file_service.py     # Document text extraction
│   └── uploads/                # Local document storage (ignored in git)
├── frontend/
│   ├── index.html              # Landing Page
│   ├── dashboard.html          # Client UI
│   ├── lawyer_dashboard.html   # Lawyer UI
│   ├── firm_dashboard.html     # Firm UI
│   ├── case_detail.html        # Unified Case Management View
│   ├── css/                    # Premium UI Styling
│   ├── js/
│   │   └── api.js              # Fetch-based API client for the Flask backend
│   └── assets/
└── README.md
```

## ⚖️ LegalDesk (SignDesk) Integration

Pocket Lawyer 2.0 uses a **Production-Grade Modular Bridge** to handle complex legal workflows like e-Signing, e-Stamping, and e-KYC.

### Architecture: The "Replaceable Proxy"
To make development and demoing easy, we have separated the API logic from the main program:

1.  **`backend/services/legal_desk_main.py`**: The **Main Orchestrator**. This handles the business logic (database, file saving, case tokens). You **never** need to change this file.
2.  **`backend/services/legal_desk_proxy.py`**: The **Replaceable API Bridge**. 
    *   **Current State**: Returns high-fidelity **Mock JSON** and simulated success messages. It handles both JSON data and **File Attachments**.
    *   **To Go Live**: Simply replace the methods in this file with real `requests.post()` calls to the SignDesk/Melento production endpoints.

### Mock Data & Testing
When using the system in "Mock Mode" (default):
- **eSign**: Accepts a signer name and a PDF attachment. Returns status `INITIATED` and a mock sandbox URL.
- **eStamp**: Simulates a 4-hour TAT (Turnaround Time) for government processing after receiving the uploaded document.
- **Drafting**: Uses the `legal_templates.py` library to generate professional 1,500+ word legal documents.

### Switching to Production
1.  Obtain your `CLIENT_ID` and `API_KEY` from [Melento.ai](https://melento.ai/) or [SignDesk.com](https://signdesk.com/).
2.  Update your `backend/config.py` with these credentials.
3.  Modify `legal_desk_proxy.py` to remove the mock return statements and implement the real fetch logic using the `requests` library.

---

## 🧪 Running a Perfect Demo

To showcase the Legal Services Hub without real API keys, use the following **Mock Values** and **Test Documents**:

### 1. Mock Test Documents
We have provided professional-grade mock documents in the `/test_documents` folder. Use these when the system asks to "Attach Document":
- `test_documents/sample_rent_agreement.pdf`
- `test_documents/sample_affidavit.pdf`
- `test_documents/sample_poa.pdf`

### 2. Required Mock Inputs
| Service | Field | Suggested Mock Value |
| :--- | :--- | :--- |
| **Aadhaar eSign** | Signer Name | `Ansh Bansal` |
| | Aadhaar (Last 4) | `1234` |
| **Digital Stamp** | State | `Delhi` |
| | Stamp Value | `100` |
| **Video KYC** | KYC Type | `Video KYC (VCIP)` |
| | Mobile Number | `+91 98765 43210` |

### 3. Resetting the Demo
To clear all mock service logs and start fresh:
1. Log out of the dashboard.
2. (Optional) Run `rm backend/uploads/*` to clear uploaded documents.

---

## 📜 License
MIT License.
