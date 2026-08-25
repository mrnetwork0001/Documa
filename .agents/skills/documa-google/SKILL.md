---
name: documa-google
description: Architecture, guidelines, Antigravity SDK specs, and Google Cloud hackathon rules for Documa (Autonomous Multimodal Audit & Procurement Fleet) built for the Google All Things Agentic Hackathon.
---

# 👁️ Documa - Google Hackathon Skill & Execution Guide

Use this skill whenever working on, reviewing, or developing **Documa** - the Autonomous Multimodal Audit & Procurement Fleet for the Google All Things Agentic Hackathon.

## 📌 Project Overview & Prize Targets
- **Target Event:** Google All Things Agentic Hackathon (Devpost)
- **Deadline:** September 1, 2026 @ 1:00 am GMT+1
- **Prize Targets:** $50,000 Grand Prize + $20,000 Taskmaster Track Winner
- **Core Stack:** Gemini 3.5 Flash + Antigravity SDK + Google Cloud Run + Firestore + Cloud Storage

## 🏗️ Technical Architecture Rules

### 1. Gemini 3.5 Multimodal Vision
- Ingest scanned receipt images, multi-page PDFs, and physical PO contracts into Gemini 3.5 Flash multimodal vision API.
- Extract structured JSON line items, tax breakdowns, and vendor metadata.

### 2. Antigravity SDK Multi-Agent Fleet
- Build modular agent classes:
  - `VisionAgent`: Multimodal document processing and data extraction.
  - `AuditorAgent`: Cross-references parsed line items against purchase orders stored in Firestore.
  - `DiscrepancyAgent`: Auto-approves compliant payouts or generates formal vendor price discrepancy reports.

### 3. Google Cloud Infrastructure Deployment
- Deploy backend worker container to **Google Cloud Run**.
- Store persistent audit state in **Firestore**.
- Store document uploads in **Google Cloud Storage**.

## 🚨 Submission Checklist
- Public GitHub repo with Apache 2.0 or MIT License.
- Architecture Diagram + step-by-step spin-up instructions in `README.md`.
- 4-minute demo video proving execution on Google Cloud (showing Cloud Run console or Vertex AI logs).
