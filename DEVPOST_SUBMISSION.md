# 🏆 DOCUMA - DEVPOST SUBMISSION MASTER KIT

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

> **Framing note.** Judging weights *Innovation & Operational Utility* at 40%, defined as
> "autonomous, high-value action over simple chat." So the video opens on the **zero-touch
> Eventarc path** - a file lands in a bucket and the fleet acts with nobody watching - and
> treats the dashboard as the *human escalation surface*, not the entry point. Clicking preset
> buttons first would frame Documa as a chatbot with extra steps.
>
> **Record with `DOCUMA_STRICT_MODE=true` set.** In strict mode Documa refuses to fall back to
> simulated fixtures, so every figure on screen is provably a live Gemini extraction. The
> `⬤ LIVE GEMINI` badge next to the audit status is the on-camera proof.

```text
⏱️ 0:00 – 0:40: THE PROBLEM
• Physical receipts on a desk; the 15+ hour weekly manual reconciliation bottleneck.
• "Documa is not a chatbot you ask. It is a fleet that already did the work."

⏱️ 0:40 – 1:40: THE AUTONOMOUS PATH (the money shot - no UI, no clicking)
• Terminal: `gsutil cp overcharged_invoice.png gs://documa-receipts-bucket/`
• Cut to the Google Cloud Run console. Show the request arriving on its own via Eventarc.
• Cloud Run logs stream live: MultimodalVisionAgent -> ContractAuditorAgent ->
  DiscrepancyDispatcherAgent. Say plainly: "Nobody clicked anything."
• Firestore console: the new audit_logs and disputes documents appearing in real time.

⏱️ 1:40 – 2:25: WHAT THE FLEET DECIDED
• Open the dashboard on that same audit - it is the review surface, not the trigger.
• Point at the ⬤ LIVE GEMINI badge: these numbers came from Gemini 3.5 Flash, not a fixture.
• Line-item variance table: $4,400.00 billed vs $3,250.00 contracted, +$1,150.00 flagged.
• This one exceeded the $500 autonomy threshold, so the fleet escalated it to a human -
  show the sign-off controls. Documa knows the limit of its own authority.

⏱️ 2:25 – 3:00: FULL AUTONOMY, END TO END (Scenario 4)
• Run the Minor Overcharge document ($3,550.00 billed vs $3,250.00 contracted).
• $300.00 variance is under threshold, so no human is involved at all: the fleet drafts and
  dispatches the formal vendor dispute notice itself. Show the generated Markdown.
• "That is the difference between an agent that reports a problem and one that resolves it."

⏱️ 3:00 – 3:35: ARCHITECTURE & ENGINEERING DISCIPLINE
• Architecture diagram: GCS -> Eventarc -> Cloud Run -> Antigravity fleet -> Firestore.
• Antigravity SDK harness with schema-enforced structured output.
• Guardrails: all 12 filesystem/shell tools disabled + deny-all policy, because invoices are
  untrusted input and a malicious document must not be able to drive tools.
• Strict mode: Documa raises rather than silently returning data it did not actually extract.

⏱️ 3:35 – 4:00: IMPACT
• 15+ hours per week of reconciliation removed; overcharges caught before payout, not after.
• Humans see only the exceptions that genuinely need a signature.
```
