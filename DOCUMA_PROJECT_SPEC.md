# 👁️ DOCUMA - Autonomous Multimodal Audit & Procurement Fleet

> **Google All Things Agentic Hackathon Master Blueprint ($180,000 Cash Pool)**  
> **Target Track:** The Taskmaster ($20,000 Track Winner / $50,000 Grand Prize Target)  
> **Core Stack:** Gemini 3.5 Flash + Antigravity SDK + Google Cloud Run + Firestore + Cloud Storage  
> **Submission Deadline:** September 1, 2026 @ 1:00 am GMT+1  
> **License:** Apache 2.0 Open Source  
> **Author:** Ifeanyichukwu Onwo (`mrnetwork`)  

---

## 📌 Executive Summary

**Documa** is an **Autonomous Multimodal Audit & Procurement Fleet** built for enterprises, startups, and finance teams using **Gemini 3.5 Flash**, the **Antigravity SDK**, and **Google Cloud Run**.

In modern organizations, procurement and finance teams handle thousands of messy physical receipts, scanned PDF contracts, bill-of-lading manifests, and invoice receipts. Manually cross-checking line items against approved purchase orders and vendor contracts is a slow, error-prone, 15+ hour weekly chore.

**Documa turns manual document audit into an autonomous background workflow:**
1. **Multimodal Vision Intake:** Users/systems drop scanned PDFs, handwritten receipts, or images into **Google Cloud Storage**.
2. **Gemini 3.5 Vision Agent:** The Antigravity Document Vision Agent leverages **Gemini 3.5's native multimodal vision** to extract structured line items, taxes, dates, and vendor signatures from complex unstructured media.
3. **Contract Auditor Agent:** Cross-references extracted totals against vendor agreements stored in **Firestore**, detecting overcharges, unapproved line items, or missing discounts.
4. **Discrepancy Dispatcher Agent:** Automatically approves compliant payouts or dispatches formal vendor price-discrepancy reports, pinging finance managers ONLY when a major anomaly requires human sign-off.

---

## 🎯 Technical Moat & Google Judging Criteria Alignment

| Judging Criteria | Weight | Implementation in Documa | Score |
| :--- | :--- | :--- | :--- |
| **Innovation & Operational Utility** | **40%** | Solves enterprise procurement friction with zero-touch background multi-agent execution. | ⭐⭐⭐⭐⭐ (5/5) |
| **Architectural Discipline & Tech Stack** | **30%** | Built with Antigravity SDK + Gemini 3.5 Flash deployed on Google Cloud Run & Firestore. | ⭐⭐⭐⭐⭐ (5/5) |
| **Demo & Production Readiness** | **30%** | Live unedited video demo + reproducible setup + Cloud Run proof. | ⭐⭐⭐⭐⭐ (5/5) |

---

## 🏗️ System Architecture & Workflow

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

## 📋 Devpost Submission Form Fill-In Answers

### 1. PROJECT NAME
`Documa`

### 2. ELEVATOR PITCH (1–2 Sentences)
`Documa is an autonomous multimodal audit and procurement fleet built with Gemini 3.5 Flash, the Antigravity SDK, and Google Cloud Run that parses scanned receipts, audits contracts against Firestore POs, and handles vendor discrepancies asynchronously.`

### 3. DETAILED PROJECT DESCRIPTION
`Procurement and finance teams lose countless hours manually auditing physical receipts, scanned PDF contracts, and vendor manifests against approved purchase orders. Documa changes that by turning document reconciliation into an autonomous, background multi-agent workflow. Built on Gemini 3.5 Flash and the Antigravity SDK, and deployed on Google Cloud Run, Documa ingests unstructured media from Cloud Storage. Its Multimodal Vision Agent leverages Gemini 3.5's vision capabilities to extract structured line items, vendor details, and signatures. The Contract Auditor Agent cross-references these details against purchase orders in Firestore to spot pricing anomalies, unapproved fees, or missing volume discounts. Documa operates asynchronously, automatically authorizing compliant payouts and surfacing to finance leaders ONLY when an unresolvable discrepancy requires human intervention.`

### 4. HOW DOES IT USE GEMINI 3.5 & ANTIGRAVITY SDK?
`Documa combines Gemini 3.5 Flash with the Antigravity SDK:
1. Gemini 3.5 Flash: Native multimodal processing of high-resolution scanned document images, handwritten receipts, and multi-page PDF contracts.
2. Antigravity SDK: Multi-agent routing, tool calling, state management, and memory persistence across background audit tasks.`

### 5. TECH STACK
`Gemini 3.5 Flash, Antigravity SDK / Google ADK, Google Cloud Run, Firestore, Google Cloud Storage, Python 3.11, Next.js 14, Tailwind CSS, TypeScript, Apache 2.0 License.`

---

## ⏱️ Technical Execution Plan (Aug 15 – Sept 1)

- **Phase 1 (Aug 15 – Aug 20):** Setup Python Antigravity SDK agent logic (`vision_agent.py`, `auditor_agent.py`).
- **Phase 2 (Aug 21 – Aug 25):** Integrate Gemini 3.5 Flash multimodal API & Firestore PO database schema.
- **Phase 3 (Aug 26 – Aug 28):** Containerize app with Docker & deploy worker daemon on Google Cloud Run.
- **Phase 4 (Aug 29 – Sept 1):** Record 4-minute demo video showing Cloud Run console, publish social post, and submit to Devpost.
