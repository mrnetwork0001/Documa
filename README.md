<div align="center">

<img src="documa/static/documa-header.png" alt="Documa - Autonomous Document Control" width="440">

**Invoices audit themselves. People only see the exceptions.**

[**Live app**](https://documa-fleet-466418539031.us-central1.run.app) ·
[Dashboard](https://documa-fleet-466418539031.us-central1.run.app/app) ·
[Documentation](https://documa-fleet-466418539031.us-central1.run.app/docs)

![Gemini 3.5 Flash](https://img.shields.io/badge/Gemini-3.5%20Flash-4285F4)
![Antigravity SDK](https://img.shields.io/badge/Antigravity-SDK-1a73e8)
![Cloud Run](https://img.shields.io/badge/Cloud%20Run-deployed-34A853)
![Firestore](https://img.shields.io/badge/Firestore-native-F9AB00)
![License](https://img.shields.io/badge/license-Apache%202.0-lightgrey)

*Google All Things Agentic Hackathon · The Taskmaster*

</div>

---

## The problem

You agreed to buy 10 monitors at **$180** each. That agreement is purchase order **PO-9921**.
The vendor invoices you at **$210**.

Catching that means someone opening the invoice, finding the PO, comparing every line, spotting
a $30-per-unit markup, and writing the dispute. Times hundreds of invoices a month. It is
**15+ hours a week** of work that finds overcharges *after* the money has left.

**Documa does the reconciliation itself and surfaces only what genuinely needs a signature.**

| Outcome | When | Human involved |
| :--- | :--- | :---: |
| `AUTO_APPROVED_PAYOUT` | No discrepancies, variance within $1 | **No** |
| `GENERATED_DISCREPANCY_REPORT` | Discrepancies, variance ≤ $500, nothing unauthorized | **No** |
| `ESCALATED_TO_HUMAN_FINANCE` | Variance > $500, unauthorized item, or no matching PO | Yes |

The **$500 threshold is the autonomy boundary**. Below it Documa drafts and dispatches the
vendor dispute itself. Above it, it stops and asks — with the evidence already assembled.
The fleet knows the limit of its own authority.

---

## Architecture

![Documa Architecture](documa/static/architecture_diagram.png)

```
Cloud Storage (a document lands)
  └─ Eventarc  object.finalized
      └─ Cloud Run worker
          ├─ Gemma triage             is this a procurement document at all?
          ├─ MultimodalVisionAgent    Gemini 3.5 Flash reads it into typed data
          ├─ ContractAuditorAgent     reconciles every line against the PO
          └─ DiscrepancyDispatcher    approves · disputes · escalates
              └─ Firestore            audit log + dispute record
```

A file arriving **is** the trigger. Three agents run as a sequential pipeline on the official
Antigravity SDK harness, each handing typed state to the next through a shared `AgentState`,
with every step recorded in an execution log returned with the response.

### Stack

| Layer | Technology |
| :--- | :--- |
| Vision | **Gemini 3.5 Flash** via **Vertex AI** — schema-enforced extraction |
| Triage | **Gemma** (`gemma-4-26b-a4b-it-maas`) via the Google GenAI SDK |
| Agents | **Antigravity SDK** (`google-antigravity`) |
| Compute | **Cloud Run** — `python:3.11-slim`, scales to zero |
| State | **Firestore** — `purchase_orders`, `audit_logs`, `disputes` |
| Intake | **Cloud Storage** — `gs://documa-receipts-bucket` |
| Triggers | **Eventarc** — `object.finalized` |
| Pipeline | **Cloud Build** + **Artifact Registry** |
| Service | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| Frontend | Hand-written HTML/CSS — no framework, no CDN, no build step |

### Hackathon requirements

| Requirement | Satisfied by |
| :--- | :--- |
| Gemini 3.5 or newer via Gemini API **or Vertex AI** | `gemini-3.5-flash` on Vertex AI, authenticated with ADC |
| At least one Google Agent Framework | **Antigravity SDK**, plus the **GenAI SDK** for triage |
| At least one Google Cloud infrastructure service | **Cloud Run**, Firestore, Cloud Storage, Eventarc |
| *Bonus:* Gemma, Veo or Lyria | **Gemma** pre-flight document triage |

---

## Quick start

```bash
git clone https://github.com/mrnetwork0001/Documa.git && cd Documa

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # add credentials — see below
PYTHONPATH=. uvicorn documa.server:app --port 8085
```

| | |
| :--- | :--- |
| Landing | http://localhost:8085/ |
| Dashboard | http://localhost:8085/app |
| Documentation | http://localhost:8085/docs |
| OpenAPI explorer | http://localhost:8085/openapi-docs |

**Documa runs with no credentials at all** — Firestore and Cloud Storage fall back to in-memory
and local disk, so the pipeline is demonstrable offline. Nothing is read from the document in
that mode, and every result says so (see [Provenance](#provenance)).

### Credentials

Either a Gemini API key in `.env`:

```
GEMINI_API_KEY=your-key
```

…or, if your organisation disallows API keys, **Application Default Credentials** against
Vertex AI — no key is stored anywhere:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

```
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
```

> **Two things bite here.** The **quota project** must be set explicitly, or requests are
> attributed to a shared Google project and every model returns `404`. And Gemini 3.x publisher
> models are served from **`global`**, not a regional endpoint — `us-central1` returns `404`
> for `gemini-3.5-flash`.

### Run the fleet from the CLI

```bash
PYTHONPATH=. python main.py                        # all four audit scenarios
PYTHONPATH=. pytest tests/test_audit_fleet.py -v   # test suite
```

### Deploy to Cloud Run

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
./deploy.sh
```

One command: enables the APIs, grants the runtime service account `aiplatform.user`,
`datastore.user` and `storage.objectViewer`, creates the Artifact Registry repository, builds
via Cloud Build, and deploys with `min-instances=0` so an idle service costs nothing.

Then wire the autonomous path:

```bash
gcloud storage buckets create gs://documa-receipts-bucket --location=us-central1

gcloud eventarc triggers create documa-intake \
  --destination-run-service=documa-fleet \
  --destination-run-path=/api/events/gcs \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=documa-receipts-bucket" \
  --location=us-central1

# Drop a document in and walk away
gcloud storage cp receipts/overcharged_invoice.png gs://documa-receipts-bucket/
```

Within ~20 seconds Firestore holds a new `EVT-` prefixed audit record. Nobody clicked anything.

### Docker, or any VPS

The container carries nothing GCP-specific:

```bash
docker build -t documa .
docker run -d -p 80:8080 -e GEMINI_API_KEY="your-key" --restart unless-stopped documa
```

---

## Configuration

| Variable | Purpose |
| :--- | :--- |
| `GEMINI_API_KEY` | Gemini API key. `GOOGLE_API_KEY` is accepted as an alias. |
| `GOOGLE_GENAI_USE_VERTEXAI` | Truthy routes the model through Vertex AI instead. |
| `GOOGLE_CLOUD_PROJECT` | Project for Firestore and Vertex AI. |
| `GOOGLE_CLOUD_LOCATION` | Model location. Use `global` for Gemini 3.x. |
| `GCS_BUCKET_NAME` | Document bucket. Defaults to `documa-receipts-bucket`. |
| `DOCUMA_VISION_MODEL` | Vision model. Defaults to `gemini-3.5-flash`. |
| `DOCUMA_TRIAGE_MODEL` | Triage model. Defaults to `gemma-4-26b-a4b-it-maas`. |
| `DOCUMA_DISABLE_TRIAGE` | Truthy skips Gemma triage entirely. |
| `DOCUMA_STRICT_MODE` | Truthy makes a failed extraction **raise** instead of falling back. |

### Provenance

Every extraction records an `extraction_mode`, surfaced through the API and shown in the
dashboard as a badge:

- **`ANTIGRAVITY_GEMINI`** — a real Gemini vision call
- **`SIMULATED_FALLBACK`** — an offline demo fixture, *not* extraction

A document matching no fixture comes back `UNKNOWN` at `$0.00` with zero confidence rather than
plausible fiction. **Run demos with `DOCUMA_STRICT_MODE=true`** — Documa then refuses to fall
back at all, so every figure on screen is provably live. The deployed service runs in strict
mode permanently.

---

## Demo scenarios

Audited against **PO-9921** — 10 monitors at $180, 5 chairs at $250, approved total **$3,250**.
Every figure below was produced by a **live Gemini extraction** on the deployed service:

| Document | Billed | Variance | Outcome | Human |
| :--- | ---: | ---: | :--- | :---: |
| `compliant_invoice.png` | $3,250.00 | $0.00 | `AUTO_APPROVED_PAYOUT` | — |
| `minor_overcharge_invoice.png` | $3,550.00 | +$300.00 | `GENERATED_DISCREPANCY_REPORT` | — |
| `unauthorized_fees_invoice.png` | $3,700.00 | +$450.00 | `ESCALATED_TO_HUMAN_FINANCE` | ✋ |
| `overcharged_invoice.png` | $4,400.00 | +$1,150.00 | `ESCALATED_TO_HUMAN_FINANCE` | ✋ |

**The minor-overcharge case is the clearest demonstration of autonomy:** a real overcharge
caught, disputed, and formally resolved with nobody in the loop.

---

## HTTP API

| Endpoint | Purpose |
| :--- | :--- |
| `POST /api/audit/process` | Audit a document by path or GCS URI |
| `POST /api/audit/upload` | Multipart upload, then audit |
| `POST /api/events/gcs` | Eventarc `object.finalized` handler |
| `GET/POST /api/po` | List / create purchase orders |
| `GET /api/audit/logs` | Audit history |
| `GET /api/disputes` | Dispute reports |
| `POST /api/disputes/{id}/approve` | Record a human finance decision |
| `GET /api/disputes/{id}/export/pdf` | Printable vendor dispute notice |
| `GET /api/audit/export/csv` | ERP-compatible CSV (SAP / QuickBooks) |
| `GET /api/stats` | Live fleet counters from the audit trail |

```bash
curl -X POST https://documa-fleet-466418539031.us-central1.run.app/api/audit/process \
  -H 'Content-Type: application/json' \
  -d '{"document_id":"DOC-MINOR-404",
       "file_path_or_url":"receipts/minor_overcharge_invoice.png",
       "po_number_override":"PO-9921"}'
```

---

## Engineering notes

**An invoice is untrusted input.** The Antigravity harness enables filesystem and shell tools by
default — unacceptable for an agent whose input is a third-party document that could carry text
aimed at the model. All twelve non-terminal tools are disabled, leaving the agent able only to
perform inference, and the prompt instructs it to treat document text as data, never
instructions.

**A cheap model screens for the expensive one.** Every document used to cost a full multimodal
extraction, invoice or not. Gemma now answers one narrow question first — *is this a procurement
document?* — and a confident no declines it before Gemini is called. Triage is advisory: failure
or unavailability never blocks an audit.

**Fail visibly, not plausibly.** The first version caught every exception and fell back to demo
data. It felt robust and was the most dangerous thing in the codebase: a broken model call was
indistinguishable from a successful one. Provenance is now a first-class field and strict mode
makes failure raise.

**The agent's record is immutable.** A finance manager's override is written to a separate
`human_decision` field, so `action_taken` remains an accurate account of what the fleet decided.
Conflating the two corrupted records and returned `500` on every subsequent read — the bug that
taught the lesson.

**Sync/async bridge.** The Antigravity SDK is async-only while the fleet is synchronous. The
bridge works both off the event loop (CLI, tests, FastAPI `def` endpoints) and on it, where a
bare `asyncio.run` would raise.

---

## Testing

```bash
PYTHONPATH=. pytest tests/test_audit_fleet.py -v
```

Covers vision extraction, PO reconciliation, all three dispatch branches, and full pipeline
orchestration. The four demo scenarios above were additionally verified end to end against live
Gemini extractions on the deployed service.

## Not production-hardened

This is a hackathon build. CORS is open to all origins and no endpoint carries authentication,
including the finance override. Put it behind your own auth before pointing it at real
procurement data.

---

<div align="center">

**[Apache 2.0](LICENSE)** · Ifeanyichukwu Onwo ([@mrnetwork0001](https://github.com/mrnetwork0001))

</div>
