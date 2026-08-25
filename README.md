# 👁️ Documa - Autonomous Multimodal Audit & Procurement Fleet

**Google All Things Agentic Hackathon ($180,000 Cash Pool / $50,000 Grand Prize Target)**

Documa is an autonomous multimodal audit and procurement fleet built with **Gemini 3.5 Flash**, **Antigravity SDK**, **Google Cloud Run**, **Google Firestore**, **Google Cloud Storage**, and **Google Eventarc**.

![Documa Architecture Diagram](documa/static/architecture_diagram.png)

---

## 🏗️ Architecture & Technology Stack

- **Multimodal AI Vision:** `gemini-3.5-flash` (`google-genai` SDK v0.1.0+) parsing receipts, invoice PDFs, unit prices, sub-totals, and vendor signatures.
- **Agent Framework:** `Antigravity SDK Engine` (`MultimodalVisionAgent` -> `ContractAuditorAgent` -> `DiscrepancyDispatcherAgent`).
- **Google Cloud Services:**
  - **Google Cloud Run:** Serverless containerized daemon (`Dockerfile`).
  - **Google Firestore:** Real-time NoSQL Purchase Order & Audit database.
  - **Google Cloud Storage:** Object bucket (`gs://documa-receipts-bucket`).
  - **Google Eventarc:** Asynchronous `object.finalized` Cloud Storage notifications.
- **Web Application & UI:** Python 3.14 + FastAPI + Stripe/Supabase Cyberpunk Glassmorphism (`dashboard.css` & `landing.css`).

---

## 🚀 Quick Spin-Up Instructions

### Option A: Local Python Environment
```bash
# 1. Clone & Enter Directory
git clone https://github.com/mrnetwork0001/Documa.git
cd Documa

# 2. Set Up Virtual Environment & Dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set Gemini API Key (Optional for API; Resilient Vision Engine Enabled)
export GEMINI_API_KEY="your-gemini-api-key"

# 4. Start Server
PYTHONPATH=. uvicorn documa.server:app --port 8085
```
Open **[http://localhost:8085/](http://localhost:8085/)** (Landing Page) or **[http://localhost:8085/app](http://localhost:8085/app)** (App Dashboard).

---

### Option B: Docker & Google Cloud Run Deployment
```bash
# Build & Run Container Locally
docker build -t documa .
docker run -p 8085:8085 -e GEMINI_API_KEY="your-key" documa

# Deploy to Google Cloud Run
./deploy.sh
```

---

## 🧪 Automated Test Suite
```bash
PYTHONPATH=. pytest tests/test_audit_fleet.py -v
```

---

## 📦 License
Licensed under the [Apache 2.0 License](LICENSE).
