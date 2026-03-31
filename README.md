# Pocket Lawyer 2.0 ⚖️

Pocket Lawyer 2.0 is a full-stack, AI-powered Legal SaaS platform. It acts as a smart, persistent case management system for Clients, Lawyers, and Law Firms. 

Unlike traditional platforms, this uses a revolutionary **"Case → Structure → Store → Continue"** paradigm powered by AI (Google Gemini / OpenAI / Anthropic) to extract structured legal Case Tokens from plain-text user input and document uploads.

---

## 🎯 Features

- **Anti-Chatbot AI Engine:** Uses strict system prompts to force AI (Gemini/OpenAI) to return structured JSON data for case analysis, risk detection, and legal guidance instead of generic chatty responses.
- **Case Token System:** Case data is serialized into versioned JSON tokens. When a client switches lawyers, the new lawyer receives the complete, structured context instantly.
- **Document AI Processing:** Upload PDF/DOCX files and the AI automatically extracts the text, summarizes it, and highlights legal risks (RED/YELLOW/GREEN).
- **Role-Based Access:** Distinct secured dashboards for Clients, Lawyers, and Firm Administrators.
- **Zero-Config Database:** Uses SQLite to store cases, chat logs, notes, timelines, and documents. No need to install PostgreSQL to run the project locally.

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
2. In the `backend` folder, duplicate the file named `config.example.py`.
3. Rename the duplicated file to exactly `config.py`.
4. Open your new `config.py` file and paste your key inside the empty string quotes on this line:
   ```python
   # Google Gemini (default)
   GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'PASTE_YOUR_KEY_HERE')
   ```
*(Note: `config.py` is safely ignored by Git so your keys won't leak when you push!)*

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

## 📜 License
MIT License.
