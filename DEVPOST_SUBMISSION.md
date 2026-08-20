# 🏆 DOCUMA — DEVPOST SUBMISSION MASTER KIT

> **Hackathon:** Google All Things Agentic Hackathon ($180,000 Cash Pool)  
> **Target Track:** The Taskmaster ($20,000 Track Winner / $50,000 Grand Prize Target)  
> **GitHub Repository:** [https://github.com/mrnetwork0001/Documa](https://github.com/mrnetwork0001/Documa)  
> **License:** Apache 2.0 Open Source  
> **Author:** Ifeanyichukwu Onwo (`mrnetwork0001`)  

---

## 📋 Devpost Submission Form Fields (Copy & Paste Ready)

### 1. PROJECT NAME
`Documa`

### 2. ELEVATOR PITCH (1–2 Sentences)
`Documa is an autonomous multimodal audit and procurement fleet built with Gemini 3.5 Flash, the Antigravity SDK, and Google Cloud Run that ingests scanned receipts, cross-audits contracts against Firestore POs, and handles vendor discrepancies asynchronously.`

### 3. DETAILED PROJECT DESCRIPTION
```text
In enterprise organizations, finance and procurement teams spend 15+ hours every week manually cross-checking physical receipts, scanned PDF contracts, and vendor manifests against approved purchase orders.

Documa turns manual document audit into an autonomous background workflow:
1. Multimodal Document Intake: Scanned PDFs, handwritten receipts, and physical invoices are dropped into Google Cloud Storage.
2. Gemini 3.5 Multimodal Vision Agent: Leverages Gemini 3.5 Flash's native vision capabilities to extract structured line items, unit prices, taxes, dates, and signatures.
3. Contract Auditor Agent: Queries Firestore for matching Purchase Orders (POs) and calculates itemized unit-price overcharges, quantity errors, and unauthorized line items.
4. Discrepancy Dispatcher Agent: Auto-approves compliant payouts, drafts formal Markdown vendor price-discrepancy reports, or escalates major anomalies to finance leaders for one-click sign-off.
```

### 4. HOW DOES IT USE GEMINI 3.5 & ANTIGRAVITY SDK?
```text
1. Gemini 3.5 Flash: Native multimodal processing of high-resolution scanned receipt images, multi-page PDFs, and physical PO contracts via google-genai SDK.
2. Antigravity SDK: Multi-agent routing, tool calling, state management, and memory persistence across background audit tasks deployed on Google Cloud Run.
```

### 5. TECH STACK
`Gemini 3.5 Flash, Antigravity SDK, Google Cloud Run, Firestore, Google Cloud Storage, Eventarc, Python 3.11, FastAPI, Tailwind CSS, Lucide Icons, Apache 2.0 License.`

---

## 🎬 4-Minute Demo Video Recording Storyboard

```text
⏱️ 0:00 – 0:45: THE PROBLEM
• Show messy scanned physical receipt images and explain the 15+ hour weekly manual audit bottleneck.
• Introduce Documa as the Autonomous Multimodal Audit Fleet built on Gemini 3.5 Flash and Google Cloud Run.

⏱️ 0:45 – 1:45: COMPLIANT RECEIPT DEMO
• Open http://localhost:8080 (Documa Web Dashboard).
• Click "Compliant Invoice" preset.
• Show Gemini 3.5 Vision Agent extracting $3,250.00 baseline.
• Highlight Auditor Agent matching PO-9921 and Discrepancy Dispatcher auto-approving immediate payout.

⏱️ 1:45 – 2:45: OVERCHARGE & UNAUTHORIZED FEE DISCOVERY
• Click "Unit Price Overcharge" preset ($4,400.00 billed vs $3,250.00 approved).
• Point to red variance badges (+ $1,150.00 overcharge).
• Show generated formal Markdown Vendor Dispute Report.
• Demonstrate Human Finance Manager sign-off controls ("Reject Overcharge" / "Pass Exception").

⏱️ 2:45 – 3:30: GOOGLE CLOUD ARCHITECTURE & LOGS
• Show gcloud run deploy execution and Cloud Run logs executing background daemon tasks.
• Show Firestore database records storing purchase orders and audit logs.

⏱️ 3:30 – 4:00: CONCLUSION & IMPACT
• Summarize how Documa saves enterprise finance teams 15+ hours weekly with zero-touch background multi-agent execution.
```
