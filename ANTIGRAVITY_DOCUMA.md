# 👁️ ANTIGRAVITY_DOCUMA — Persistent Project Context Directive

> **Project Name:** DOCUMA  
> **Target Hackathon:** Google All Things Agentic Hackathon ($180,000 Cash Pool)  
> **Target Track:** The Taskmaster ($20,000 Track Winner / $50,000 Grand Prize Target)  
> **Submission Deadline:** September 1, 2026 @ 1:00 am GMT+1  
> **Primary LLM:** Gemini 3.5 Flash  
> **Primary Agent Framework:** Antigravity SDK  
> **Cloud Infrastructure:** Google Cloud Run + Firestore + Cloud Storage  
> **Assistant Engine:** Antigravity AI Assistant  

---

## 📌 Core Directives for Documa Development

1. **Master Spec Source of Truth:**  
   Always consult [DOCUMA_PROJECT_SPEC.md](file:///Users/mrnetwork/Documa/DOCUMA_PROJECT_SPEC.md).

2. **Technical Architecture Guidelines:**
   - **Gemini 3.5 Flash (Multimodal Vision):** Native processing of scanned PDFs, handwritten receipts, and PO documents.
   - **Antigravity SDK (Agent Framework):** Modular multi-agent coordination (`vision_agent.py`, `auditor_agent.py`, `discrepancy_agent.py`).
   - **Google Cloud Services (Mandatory):** Deploy backend worker to **Google Cloud Run**, store document metadata in **Firestore**, and archive files in **Cloud Storage**.

3. **Submission Requirements Checklist:**
   - Public GitHub repository with Apache 2.0 or MIT License.
   - `README.md` + Architecture Diagram + Spin-up instructions.
   - 4-minute demo video proving execution on Google Cloud (showing Cloud Run console or Vertex AI logs).

4. **Repository Key Files:**
   - Master Blueprint: `DOCUMA_PROJECT_SPEC.md`
   - Directive File: `ANTIGRAVITY_DOCUMA.md`
   - Skill Instructions: `.agents/skills/documa-google/SKILL.md`
