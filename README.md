# 👁️ Documa — Autonomous Multimodal Audit & Procurement Fleet

> Built for the **Google All Things Agentic Hackathon** ($180,000 Cash Pool / $50,000 Grand Prize Target)  
> **Target Track:** The Taskmaster ($20,000 Track Winner)  
> **Core Stack:** Gemini 3.5 Flash + Antigravity SDK + Google Cloud Run + Firestore + Cloud Storage  
> **License:** Apache 2.0 Open Source  

---

## 📌 Executive Summary

**Documa** is an autonomous multi-agent procurement and audit fleet that turns tedious, manual invoice and receipt auditing into a zero-touch background workflow.

Procurement and finance teams handle thousands of physical receipts, scanned PDF contracts, and vendor manifests. Manually cross-checking line items against purchase orders takes 15+ hours per week. Documa automates this end-to-end:

1. **Multimodal Vision Intake:** Users/systems drop scanned PDFs, receipts, or invoices into **Google Cloud Storage**.
2. **Gemini 3.5 Vision Agent:** Uses **Gemini 3.5 Flash multimodal vision** to extract itemized line items, unit prices, taxes, dates, and vendor signatures.
3. **Contract Auditor Agent:** Cross-references extracted line items against approved purchase orders stored in **Firestore**, detecting price inflation, quantity mismatches, and unapproved fees.
4. **Discrepancy Dispatcher Agent:** Automatically authorizes compliant payouts, drafts formal vendor price-discrepancy reports, or escalates major anomalies to finance leaders.

---

## 🏗️ Architecture & Multi-Agent Workflow

```
                                  ┌──────────────────────────────┐
                                  │ Scanned Receipts / PDFs / POs│
                                  └──────────────┬───────────────┘
                                                 │
                                                 │ Upload / Webhook Event
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │     Google Cloud Storage      │
                                  └───────────────┬───────────────┘
                                                 │
                                                 │ Triggers Background Worker
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │   Documa Antigravity Fleet    │
                                  │    (Google Cloud Run Worker)  │
                                  └───────────────┬───────────────┘
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   │                             │                             │
                   ▼                             ▼                             ▼
     [ Agent 1: Multimodal Vision ]   [ Agent 2: Contract Auditor ]   [ Agent 3: Discrepancy Filer ]
     • Gemini 3.5 Vision Extraction   • Cross-checks Firestore POs    • Auto-approves compliant payouts
     • Itemized Data Parsing          • Detects Overcharges & Fees    • Dispatches Vendor Dispute Reports
                   │                             │                             │
                   └─────────────────────────────┼─────────────────────────────┘
                                                 │
                                                 │ Surfaces ONLY when major anomaly occurs
                                                 ▼
                                  ┌───────────────────────────────┐
                                  │ Human Finance Approval Alert  │
                                  │ "Overcharge detected ($450)"  │
                                  │  [ Approve Dispute ] [ Pass ] │
                                  └───────────────────────────────┘
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`)
- Gemini API Key (`GEMINI_API_KEY`) or GCP Service Account Credentials

### 2. Installation
```bash
git clone https://github.com/mrnetwork/Documa.git
cd Documa
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run CLI Execution Demo
```bash
python main.py
```

### 4. Run Automated Test Suite
```bash
pytest tests/test_audit_fleet.py -v
```

### 5. Launch Cloud Run Web Daemon Locally
```bash
python -m uvicorn documa.server:app --reload --port 8080
```
Then access:
- Health check: `http://localhost:8080/health`
- Active POs: `http://localhost:8080/api/po`
- Audit logs: `http://localhost:8080/api/audit/logs`
- Discrepancy reports: `http://localhost:8080/api/disputes`

---

## ☁️ Google Cloud Run Deployment

To build and deploy the container daemon to Google Cloud Run:

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GCP_REGION="us-central1"
chmod +x deploy.sh
./deploy.sh
```

---

## 📄 License
Apache 2.0 Open Source
