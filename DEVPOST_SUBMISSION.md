# DOCUMA - DEVPOST SUBMISSION KIT

> **Hackathon:** Google All Things Agentic Hackathon
> **Track:** The Taskmaster
> **Repository:** https://github.com/mrnetwork0001/Documa
> **License:** Apache 2.0
> **Author:** Ifeanyichukwu Onwo (`mrnetwork0001`)

Everything below is copy-paste ready for the Devpost submission form.

---

## 1. PROJECT NAME

```
Documa
```

## 2. ELEVATOR PITCH

```
Documa is an autonomous audit fleet that reads vendor invoices with Gemini 3.5 Flash, reconciles every line against your contracted purchase orders in Firestore, and clears or disputes them itself - escalating to a human only when the money genuinely warrants it.
```

## 3. FEATURES AND FUNCTIONALITY

```
THE PROBLEM

You agree to buy 10 monitors at $180 each. That agreement is a purchase order. The
vendor then invoices you at $210 each. Someone in finance has to open the invoice,
find the PO, compare every line, spot the $30-per-unit markup, and write the dispute.
Multiply by hundreds of invoices a month and that is 15+ hours a week of work that
catches overcharges only after payment has already gone out.

WHAT DOCUMA DOES

Documa turns that reconciliation into an autonomous background workflow. A document
landing in a Cloud Storage bucket is the trigger - there is no button to press.

  1. GEMMA PRE-FLIGHT TRIAGE
     A cheap open Gemma model screens the document first: is this a procurement
     document at all? A confident "no" declines it before a full multimodal
     extraction is paid for.

  2. MULTIMODAL VISION AGENT
     Gemini 3.5 Flash reads the document into a schema-enforced extraction: vendor,
     line items, unit prices, tax, totals, and whether a signature is present.
     Works on scanned receipts, invoice photographs, and multi-page PDFs.

  3. CONTRACT AUDITOR AGENT
     Fetches the matching purchase order from Firestore and reconciles every billed
     line against its contracted rate, matching by SKU first then description. Flags
     price inflation, quantity mismatches, and line items no PO ever approved.

  4. DISCREPANCY DISPATCHER AGENT
     Decides the outcome and writes the document that carries it out - a payout
     authorisation, a formal vendor dispute notice with the credit-memo amount already
     calculated, or a finance escalation with reject/approve controls.

THE AUTONOMY BOUNDARY

The $500 variance threshold is the heart of the design:

  - No discrepancies, variance within $1        -> AUTO_APPROVED_PAYOUT, no human
  - Discrepancies, variance <= $500             -> GENERATED_DISCREPANCY_REPORT, no human
  - Variance > $500, unauthorised item, no PO   -> ESCALATED_TO_HUMAN_FINANCE

Below the line Documa resolves the dispute itself, start to finish. Above it, it stops
and asks a person - with the evidence already assembled. People stop reviewing invoices
and start reviewing exceptions.

ALSO INCLUDED

  - Web dashboard with drag-and-drop intake, live agent pipeline status, an itemised
    variance table, and one-click human sign-off
  - Full documentation site at /docs
  - ERP-compatible CSV export (SAP / QuickBooks) and printable PDF dispute notices
  - Complete REST API with an OpenAPI schema
  - Provenance labelling on every extraction, and a strict mode that refuses to
    fall back to demo data
```

## 4. TECHNOLOGIES USED

```
Gemini 3.5 Flash (gemini-3.5-flash) via the Gemini API / Vertex AI - multimodal vision
Gemma (gemma-3-27b-it) via the Google GenAI SDK - pre-flight document triage
Google Antigravity SDK (google-antigravity) - agent harness, schema-enforced output
Google Cloud Run - serverless container, python:3.11-slim
Google Firestore - purchase orders, audit logs, dispute records
Google Cloud Storage - document intake bucket
Google Eventarc - object.finalized triggers
Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Pillow, pytest
Frontend: hand-written HTML and CSS - no framework, no CDN, no build step
Apache 2.0
```

## 5. OTHER DATA SOURCES USED

```
None external. Documa operates on two data sources, both internal:

  1. Purchase orders held in Firestore - the contracted baseline every invoice is
     judged against. Two are seeded on startup (PO-9921 Acme Industrial Tech,
     PO-8810 Global Logistics Corp).

  2. The vendor documents themselves. The four demo invoices in receipts/ are
     synthetic, generated programmatically by documa/sample_data/generate_receipt_images.py
     so anyone can reproduce them - no real vendor or customer data is used anywhere
     in the project.
```

## 6. FINDINGS AND LEARNINGS

```
GRACEFUL DEGRADATION CAN BE A LIABILITY

The first version caught every exception and fell back to demo data. It felt robust and
it was the most dangerous thing in the codebase: a broken model call was indistinguishable
from a successful one, and any unrecognised upload came back as a confident $3,250 invoice
that had never been read. Fabricated data that looks successful is worse than a visible
failure.

The fix was to make provenance a first-class field. Every extraction now records whether
it came from a live Gemini call or a simulated fixture, the API returns it, the dashboard
shows it as a badge, and a strict mode makes failure raise instead of degrade. Unreadable
documents come back as UNKNOWN at $0.00 with zero confidence rather than plausible fiction.

WIRING UP A BUTTON FOUND A DATA-CORRUPTION BUG

The human sign-off control displayed "audit status updated in Firestore" without calling
any API. Connecting it to the real endpoint immediately broke the application: the handler
wrote the human's ruling into action_taken, a field typed to an enum that has no such
member, so one click permanently corrupted the record and every later read returned 500.

The root error was conceptual - conflating "what the fleet decided" with "what a human
later ruled". They are different facts with different lifetimes. Separating them into
action_taken and human_decision fixed the bug and produced a better audit trail, because
you can now see the agent's call and the override side by side. A UI that only pretends
to do something hides the bugs in the thing it is pretending to do.

AN INVOICE IS UNTRUSTED INPUT

The Antigravity harness enables filesystem and shell tools by default, which is sensible
for a coding agent and unacceptable for one whose input is a third-party document. A
malicious invoice could carry text aimed at the model rather than the reader. Documa
disables all twelve non-terminal tools behind a deny-all policy so the vision agent can
only perform inference, and instructs the model to treat document text as data. Threat
modelling the input, not just the output, changed the architecture.

CHEAP MODELS EARN THEIR PLACE IN FRONT OF EXPENSIVE ONES

Every document reaching the fleet cost a full multimodal extraction, whether it was an
invoice or a photograph someone dropped in the bucket by mistake. Putting an open Gemma
model in front to answer one narrow question - is this a procurement document at all? -
declines non-procurement input before the expensive call. It is advisory by design:
triage failing never blocks an audit. Model selection turned out to be an architectural
decision, not just a quality one.

AUTONOMY NEEDS A STATED BOUNDARY

The hardest design question was not what the agent could do but what it should do without
asking. An agent that escalates everything is a filter, not an agent; one that escalates
nothing is reckless with someone else's money. Making the threshold explicit, configurable
and visible in the UI turned "how autonomous is it?" from a vague claim into a number a
finance team can actually agree to.

TESTING THE BROWSER, NOT THE STYLESHEET

Several UI bugs turned out not to be bugs. Headless Chrome ignored the window size for
layout, so a mobile screenshot was really a desktop render cropped - which looked exactly
like broken CSS. Driving the browser over the DevTools protocol with real device emulation,
and measuring scrollWidth against clientWidth instead of eyeballing screenshots, replaced
guesswork with evidence. Separately, three "broken UI" reports turned out to be a stale
cached stylesheet; stamping asset URLs with file mtimes ended that whole class of problem.
```

---

## 7. DEMO VIDEO STORYBOARD (~4 minutes)

> **Framing.** Innovation & Operational Utility is 40% of the score and rewards autonomous
> action over chat. So the video opens on the **zero-touch Eventarc path** - a file lands in a
> bucket and the fleet acts with nobody watching - and treats the dashboard as the *escalation
> surface*, not the entry point. Opening on button-clicking would frame Documa as a chatbot
> with extra steps.
>
> **Record with `DOCUMA_STRICT_MODE=true`.** Documa then refuses to fall back to simulated
> fixtures, so every figure on screen is provably a live Gemini extraction. The
> `LIVE GEMINI` badge beside the audit status is the on-camera proof.

```text
0:00 - 0:40  THE PROBLEM
  - A purchase order says $180 per monitor. The invoice says $210.
  - Someone has to catch that, on every invoice, every month. 15+ hours a week.
  - "Documa is not a chatbot you ask. It is a fleet that already did the work."

0:40 - 1:40  THE AUTONOMOUS PATH  (the money shot - no UI, no clicking)
  - Terminal: gsutil cp overcharged_invoice.png gs://documa-receipts-bucket/
  - Cut to the Cloud Run console: the request arrives on its own via Eventarc.
  - Logs stream: Gemma triage -> MultimodalVisionAgent -> ContractAuditorAgent
    -> DiscrepancyDispatcherAgent. Say it plainly: "Nobody clicked anything."
  - Firestore console: new audit_logs and disputes documents appearing live.

1:40 - 2:25  WHAT THE FLEET DECIDED
  - Open the dashboard on that audit - the review surface, not the trigger.
  - Point at the LIVE GEMINI badge: these numbers came from the model, not a fixture.
  - Variance table: $4,400.00 billed vs $3,250.00 contracted, +$1,150.00 flagged.
  - Over the $500 threshold, so it escalated. Show the sign-off controls.
    "Documa knows the limit of its own authority."

2:25 - 3:00  FULL AUTONOMY, END TO END
  - Run the minor overcharge: $3,550.00 billed vs $3,250.00 contracted.
  - $300 is under threshold, so no human is involved at all - the fleet drafts and
    dispatches the vendor dispute notice itself. Show the generated Markdown.
  - "That is the difference between an agent that reports a problem and one that
    resolves it."

3:00 - 3:35  ARCHITECTURE & ENGINEERING DISCIPLINE
  - Architecture diagram: GCS -> Eventarc -> Cloud Run -> fleet -> Firestore.
  - Gemma triage in front of Gemini: cheap model screens, expensive model extracts.
  - Guardrails: all twelve filesystem and shell tools disabled behind a deny-all
    policy, because invoices are untrusted input.
  - Strict mode: Documa raises rather than returning data it did not actually read.

3:35 - 4:00  IMPACT
  - 15+ hours a week of reconciliation removed. Overcharges caught before payout.
  - Humans see only the exceptions that genuinely need a signature.
```

---

## 8. SUBMISSION CHECKLIST

- [x] Public GitHub repository, Apache 2.0
- [x] Spin-up instructions in `README.md`
- [x] Architecture diagram (`documa/static/architecture_diagram.png`, source `architecture.svg`)
- [x] Text description, technologies, data sources, findings and learnings (above)
- [ ] **Deploy to Cloud Run and capture console proof**
- [ ] **Record the ~4 minute demo video**
- [ ] Hosted URL (optional but encouraged)
- [ ] Social post with `#AllThingsAgenticHackathon` - draft in `SOCIAL_POST.md`
- [ ] Blog / content post (bonus)
- [x] Google AI model integration beyond Gemini (bonus) - Gemma triage

## 9. REQUIREMENTS MAPPING

| Requirement | How Documa meets it |
| :--- | :--- |
| Gemini 3.5 or newer via Gemini API / Vertex AI | `gemini-3.5-flash` for multimodal vision extraction |
| At least one Google Agent Framework | Antigravity SDK (`google-antigravity`); GenAI SDK for Gemma triage |
| At least one Google Cloud infrastructure service | Cloud Run, Firestore, Cloud Storage, Eventarc |
| Bonus: Gemma / Veo / Lyria | Gemma pre-flight document triage |
