# Documa — 4-Minute Demo Script

**Read the bold text aloud. The indented lines are what you do.**
Total ~3:50. Aim to finish under 4:00.

---

## BEFORE YOU HIT RECORD

- [ ] Four tabs open: **app**, **Cloud Run → Logs** (filter box: type `Agent`), **Firestore → audit_logs**, **Terminal**
- [ ] Terminal ready: `cd ~/Documa` and `export PATH="$HOME/google-cloud-sdk/bin:$PATH"`
- [ ] App hard-reloaded (⌘⇧R), then click **Reset** so it starts clean
- [ ] Do Not Disturb on (⌥-click the menu bar clock)
- [ ] `~/Downloads/live-demo-invoice.png` and `~/Downloads/not-an-invoice.png` exist
- [ ] QuickTime → File → New Screen Recording → microphone selected

**Every audit takes 12–25 seconds of real Gemini inference. That is not lag — talk through it.**

---

## 0:00 – 0:35 · THE PROBLEM

> *On screen: the Documa landing page.*

**"You agree to buy ten monitors at a hundred and eighty dollars each. That agreement is a purchase order. Then the vendor invoices you at two hundred and ten."**

**"Catching that means somebody opening the invoice, finding the purchase order, comparing every line, and writing the dispute. Times hundreds of invoices a month. That's fifteen hours a week — and it finds overcharges after the money has already gone out."**

**"Documa is not a chatbot you ask about invoices. It's a fleet that has already done the work. Let me show you what I mean by that."**

---

## 0:35 – 1:35 · THE AUTONOMOUS PATH ← *the most important minute*

> *Switch to Terminal.*

**"I'm going to drop an invoice into a Cloud Storage bucket. I'm not going to open the app. I'm not going to click anything."**

> *Type and run:*
> ```
> gcloud storage cp receipts/overcharged_invoice.png gs://documa-receipts-bucket/
> ```

**"That's it. That file arriving is the trigger."**

> *Switch to the Cloud Run Logs tab. Hit Refresh if needed.*

**"Eventarc has picked up the object-finalized event and woken the Cloud Run service. Watch the logs."**

> *Point at the lines as they appear.*

**"Gemma screens the document first — is this a procurement document at all. Then the Multimodal Vision Agent reads it with Gemini 3.5 Flash. Then the Contract Auditor reconciles it against the purchase order in Firestore. Then the Dispatcher decides what to do about it."**

> *Point at the harness-ready line.*

**"And there's the proof of the stack — Gemini 3.5 Flash, via Vertex AI, on the Antigravity SDK. That's Google's own console, not my slides."**

> *Switch to the Firestore tab. Refresh.*

**"And here's the record it wrote. Note the document ID starts with E-V-T. That prefix is only ever assigned by the Eventarc handler. Nobody touched this."**

---

## 1:35 – 2:20 · WHAT THE FLEET DECIDED

> *Switch to the app, /app. Click the **Unit Price Overcharge** preset.*

**"Now the same audit, but where a human would actually look at it. This is the review surface — not the trigger."**

> *While it runs (~15s):*

**"That pause is real multimodal inference. Gemini is reading the pixels of a scanned invoice and returning structured line items — not OCR, not a template."**

> *When it completes, point at the badge.*

**"Live Gemini, ninety-eight percent. This deployment runs in strict mode, which means it physically cannot show me a simulated number. If the model were unreachable, I'd get an error — not a plausible invoice."**

> *Point at the variance and the table.*

**"Four thousand four hundred billed against three thousand two hundred and fifty contracted. Eleven hundred and fifty dollars of overcharge, itemised line by line."**

> *Point at the sign-off buttons.*

**"That's over the five hundred dollar threshold, so the fleet stopped and escalated — with the evidence already assembled. Documa knows the limit of its own authority."**

---

## 2:20 – 3:00 · FULL AUTONOMY

> *Click **Minor Overcharge**.*

**"Now the case I'm proudest of. Same pipeline, smaller number."**

> *When it completes:*

**"Three hundred dollars of overcharge. Under the threshold — so no human is involved at all. The fleet drafted the formal vendor dispute notice itself, calculated the credit memo, and filed it."**

> *Point at the Markdown output.*

**"That's the difference between an agent that reports a problem and one that resolves it."**

---

## 3:00 – 3:25 · YOUR OWN DOCUMENT

> *Click **Reset**. Drag `~/Downloads/not-an-invoice.png` onto the dropzone.*

**"It also knows what not to spend money on. This is a poster, not an invoice."**

> *When it returns:*

**"Gemma declined it before the expensive vision call ever ran. Cheap model in front of the expensive one — that's a cost decision baked into the architecture."**

> *Click **Reset**. Drag `~/Downloads/live-demo-invoice.png` in.*

**"And here's a document the system has never seen."**

> *When it completes:*

**"Three thousand four hundred billed, a hundred and fifty dollars over contract — caught, disputed, resolved. Nothing about this one was staged."**

---

## 3:25 – 3:50 · CLOSE

> *Scroll to the architecture diagram in /docs, or show the landing page.*

**"Cloud Storage, Eventarc, Cloud Run, Firestore. Gemini 3.5 Flash for vision, Gemma for triage, three agents on the Antigravity SDK. Scaled to zero when idle."**

**"Fifteen hours a week of reconciliation, removed. Overcharges caught before payout instead of after. And a finance team that only ever sees the exceptions that genuinely need a signature."**

**"That's Documa. Thanks for watching."**

---

## IF SOMETHING GOES WRONG

| Problem | Do this |
| :--- | :--- |
| Audit seems stuck | Keep talking. Give it 30s. Gemini is genuinely slow on images. |
| Badge says SIMULATED FIXTURE | Stop recording — tell me. It should be impossible in production. |
| Logs not appearing | Hit **Refresh** in the Cloud Run logs panel. |
| Firestore shows nothing | Refresh the page; give Eventarc ~20s. |
| You fumble a line | Keep going. One clean take beats three careful ones. |

**Numbers to get right:** $180 contracted · $210 billed · $3,250 approved · $4,400 billed · +$1,150 · +$300 · +$150 · $500 threshold
