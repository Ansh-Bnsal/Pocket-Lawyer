# ⚖️ POCKET LAWYER: MASTER PROJECT MANIFEST
**"The Genetic Code of Legal Clarity & Case Continuity"**

This document tracks the complete DNA of the Pocket Lawyer platform. It contains every non-technical vision, user-interaction rule, and technical architectural decision made since Day 1.

---

## 🌎 PART 1: THE SOUL (Vision & Logic)

### 1.1 The Core Mission
**Problem:** Legal cases fail due to "Data Fragmentation" and "Lawyer Turnover." When a lawyer changes, the case knowledge restarts from zero. Information from clients is often unstructured and messy.
**Solution:** A persistent, AI-powered Case Management system that transforms raw stories into structured "Digital Assets." The system ensures **Case Continuity**—a digital thread that survives regardless of who is handling the case.

### 1.2 The "Case" as the Primary Object
In this project, the **Case** is the universe. Every Chat Session, every Document, and every AI Service is a child of the Case. 
- **Persistence**: A Case never dies. It stores its own AI summaries, timelines, and document vaults.
- **Context-Awareness**: The AI "knows" which Case it is currently analyzing, allowing for deep, relevant advice.

### 1.3 User Categories & Dynamics

| Role | Primary Value | Key Features |
|:---|:---|:---|
| **Client** | Clarity & Guidance | Natural Voice/Text input, Risk-Aware simplified document analysis, direct service booking. |
| **Private Lawyer** | Efficiency & Structuring | AI-summarized case files, pre-hearing preparation tools, automated drafting suggestions. |
| **Law Firm** | Team Management | Multi-lawyer case assignment, workload balancing, firm-wide case pools. |

**Combined Interaction:**
- A **Client** initiates a "Transient" chat. 
- AI detects a "Case-Worthy" matter and suggests **Promotion**.
- Once Promoted, the Client can invite a **Lawyer** or a **Firm** to the Case.
- A **Firm Admin** can then assign that Case to a specific **Lawyer** in their team.

---

## 🛠️ PART 2: THE FEATURES (Functional Universe)

### 2.1 Multimodal AI Assistant
- **Mode 1 (Chat)**: Professional legal strategy based on Indian Statutes (IPC, NI Act, etc.).
- **Mode 2 (Doc Analysis)**: Instant 3-tier risk detection (High/Medium/Low).
- **Mode 3 (Hybrid)**: Discussing a document in real-time while a background worker calculates technical risks.

### 2.2 The Smart Cart (Intent Engine)
The AI doesn't just talk; it **acts**.
- **Extraction**: AI identifies if a user needs an E-Sign, E-Stamp, or Rent Agreement.
- **Promotion**: It moves "Actionable Items" into the Side-Cart for one-click execution.

### 2.3 The Digital Vault
- A secure repository for every file uploaded to a case, automatically categorized by the AI.

---

## 💻 PART 3: THE MACHINE (Technical Architecture)

### 3.1 Software Stack
- **Backend**: Python (Flask) using a modular **Blueprint** structure.
- **Frontend**: Pure Vanilla (HTML5, Vanilla CSS, JS). No heavy frameworks to ensure maximum speed and "Single-File" portability.
- **Database**: **SQLite** with a relational schema for local-first reliability.

### 3.2 AI Orchestration (Stability 32.0 Standard)
We escaped the "Multi-Key Mess" by standardizing on a **Single-Key Burst Architecture**:
- **Model**: `gemini-1.5-flash` (Stable).
- **The Burst Shield**: All background workers (Intent/Risk) are staggered by **500ms and 1000ms** delays. This allows a single API key to handle 3 simultaneous workers without 429 errors.
- **Safety Bypass**: Every request includes `BLOCK_NONE` safety settings to prevent legal-advice censorship ("Null Text" fix).

### 3.3 UX Synchronization (Stability 32.4 Standard)
- **The Thinking Dots**: The frontend `typing-indicator` is synced to the SSE stream. It remains visible during the initial 0.5s "Reasoning Gap" and only disappears when the first real word arrives.

### 3.4 Networking & Security (Stability 39.0 Standard)
- **Direct File Access**: The server CORS is "Truly Open" (`*`) to allow developers to open `index.html` directly as a file (`file://`).
- **Auth Bouncer**: The `require_auth` decorator allows `OPTIONS` (Preflight) requests to pass through without a token to prevent browser security crashes.

---

## 🧬 PART 4: SYSTEM REPLICATION (Day 0 Instructions)

If starting this project from scratch:
1.  **Initialize Flask**: Use `app.py` in the root and register blueprints for `auth`, `chat`, `case`, and `services`.
2.  **Database**: Run `init_db()` to create `users`, `cases`, `chat_sessions`, `chat_messages`, and `case_services`.
3.  **Config**: Set `GEMINI_API_KEY` in `backend/config.py`.
4.  **Frontend**: Serve the `frontend/` directory. Ensure `api.js` points to `127.0.0.1:5000` for `file://` compatibility.
5.  **The Bouncer**: Ensure `auth_routes.py` ignores `OPTIONS` requests for preflight stability.

---
**End of Master Manifest.**
