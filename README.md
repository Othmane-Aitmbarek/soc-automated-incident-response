# SOC Automated Incident Response Pipeline

Final-year engineering project (PFA) — an end-to-end automated pipeline that detects suspicious process activity on a Windows host, enriches it, uses an LLM for behavioral triage, and opens/notifies an incident automatically.

## Architecture

```
Windows 11 VM (Sysmon, Event ID 1)
        │
        ▼
Wazuh Manager  ── custom detection rules (100002, 92027)
        │
        ▼
Shuffle SOAR  ── webhook trigger
        │
        ▼
SHA256 hash extraction ── VirusTotal enrichment
        │
        ▼
Groq LLM (openai/gpt-oss-120b) ── behavioral analysis of the payload
        │
        ▼
TheHive ── incident ticket created
        │
        ▼
Python sanitization ── clean Markdown/JSON into a readable summary
        │
        ▼
Email notification (SMTP) ── analyst alerted
```

## Stack

| Component | Role |
|---|---|
| Windows 11 VM + Sysmon | Target host, process creation telemetry (Event ID 1) |
| Wazuh Manager | Log collection, custom rule-based detection |
| Shuffle SOAR | Workflow orchestration |
| VirusTotal | Hash reputation enrichment |
| Groq LLM API (`openai/gpt-oss-120b`) | AI-assisted behavioral analysis of obfuscated payloads |
| TheHive | Centralized incident ticketing |
| SMTP | Email notification to the analyst |

## Detection scenarios tested

The pipeline was validated end-to-end against multiple scenario types, mapped to MITRE ATT&CK:

- **Credential dumping (Mimikatz)** — `mimikatz.exe` executed from a user's Downloads folder, detected by Wazuh Rule `100002`, tagged **T1003** (Credential Dumping). Correctly flagged **Malicious/Suspicious**, case auto-created in TheHive, analyst notified by email with forensic details (process image, command line, SHA256 hash).
- **Obfuscated PowerShell execution** — Living-off-the-Land commands using `-EncodedCommand` / `-ExecutionPolicy Bypass`, mapped to **T1059.001** (PowerShell) and **T1027** (Obfuscated Files or Information). Correctly flagged **Suspicious/Malicious**.
- **Benign administrative command** (`Get-Process`) — correctly classified as **Benign**, no incident created.

No false positives were observed across the tested scenarios. This constitutes an initial functional validation rather than a statistically representative false-positive rate — a larger scenario set and timing measurements would be needed for that.

## Technical challenges solved

- **Duplicate webhooks** — consolidated multiple Wazuh `ossec.conf` integration blocks into a single block scoped to specific `<rule_id>` values, removing broad `<level>`-based triggers that caused duplicate alerts. See [`wazuh-config/ossec_shuffle_integration.conf`](./wazuh-config/ossec_shuffle_integration.conf).
- **JSON payload formatting** — fixed malformed JSON in the Shuffle → email step using Liquid's `escape` filter.
- **Readable email summaries** — the Groq LLM returns Markdown/JSON-ish text; [`scripts/sanitize_llm_output.py`](./scripts/sanitize_llm_output.py) strips formatting artifacts and normalizes section headers before the summary is emailed.

## Repository structure

```
├── diagram/              Architecture diagram
├── screenshots/          Wazuh alert, TheHive case, Shuffle workflow canvas, email output
├── shuffle-workflow/      Exported Shuffle workflow (SOC-Auto_Project.json, secrets redacted)
├── wazuh-config/          ossec.conf integration block used to forward alerts to Shuffle
└── scripts/               Python script used to sanitize LLM output for email
```

**Note:** All credentials, API keys, IPs, and webhook IDs in the exported files have been replaced with placeholders (e.g. `YOUR_GROQ_API_KEY_HERE`). No real secrets are included in this repository.

## Screenshots

| | |
|---|---|
| Wazuh alert (Mimikatz detection) | `screenshots/01_wazuh_mimikatz_detection.png` |
| TheHive incident opened | `screenshots/02_thehive_incident_open.png` |
| TheHive case list | `screenshots/03_thehive_incident_list.png` |
| Shuffle SOAR workflow canvas | `screenshots/04_shuffle_soar_workflow.png` |
| Email notification | `screenshots/05_email_notification.png` |

