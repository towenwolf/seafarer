# Seafarer — Sprint 1 README

## Overview

Seafarer is a deterministic ETL service designed to be used as a tool by agents, not as an autonomous agent.  
Sprint 1 delivers a fully local, Docker-based proof of concept demonstrating safe, agent-orchestrated data movement.

A sailing metaphor is used for naming only; behavior, schemas, and guardrails are strictly deterministic and machine-oriented.

---

## Core Metaphor

| Concept | Name |
|------|------|
| Core service | Seafarer |
| CLI | seafarer |
| Connectors | Ports |
| Plan | Chart |
| Execution | Voyage |
| State | Logbook |
| Policy | Maritime rules |

---

## Sprint 1 Goal

Demonstrate an end-to-end voyage:

**CSV in Blob emulator (source port) → Parquet in Blob emulator (sink port)**

The voyage must be orchestrated by an external agent-runner using only the Seafarer CLI.

---

## Definition of Done

A scripted agent can execute the following sequence without manual steps:

```bash
seafarer agent plan --task task.json --json
seafarer agent validate --chart chart.json --json
seafarer agent execute --chart chart.json --json
```

**Success criteria**
- Parquet written to sink blob emulator  
- JSON manifests emitted for each phase  
- Deterministic exit codes  

---

## Architectural Constraints

- Seafarer core image must not include infra  
- No blob emulators  
- No agent-runner  
- Infra components exist only for testing  
- Ports must work against real Blob endpoints by configuration change only  

---

## Required Repository Layout

```text
seafarer/
  core/
  cli/
  ports/
    blob_csv_source/
    blob_parquet_sink/

infra/
  compose/
    blob-source/
    blob-sink/
  agent/

examples/
  task.json
  pipeline.yaml
  policy.yaml (optional)
```

---

## Infra Components (External)

### Blob Source Emulator
- Hosts CSV input files  
- Separate container, port, and volume  
- Seed script uploads a sample CSV  

### Blob Sink Emulator
- Receives Parquet output  
- Separate container, port, and volume  
- Validation script checks Parquet exists and is non-empty  

### Agent Runner
- Scripted “navigator” (no LLM calls)  
- Executes plan → validate → execute  
- Captures JSON outputs to `/workspace/agent_runs/`  

---

## Core Service Responsibilities (Seafarer)

### Required CLI Commands

```bash
seafarer agent capabilities --json
seafarer agent plan --task <task.json> --json
seafarer agent validate --chart <chart.json> --json
seafarer agent execute --chart <chart.json> --json
```

All commands must be:
- Non-interactive  
- Single JSON output  
- Deterministic exit codes  

---

## Output Contract (Minimum)

All JSON responses must include:

```json
{
  "status": "success|error",
  "errors": [],
  "metrics": {},
  "artifacts": []
}
```

Plan and execute outputs must also include `chart_id` or `run_id`.

---

## Logbook (State)

- Stored at `/state`  
- Implemented with SQLite or DuckDB  
- Tracks processed files and voyage metadata  
- Must support replayability  

---

## Maritime Rules (Policy)

- Loaded from `/workspace/policy.yaml`  
- Enforces:
  - Allowed ports  
  - Read vs write permissions  
  - Max rows or runtime limits  
- Writes are dry-run by default unless policy explicitly allows execution  

---

## Ports (Connectors)

### blob_csv_source
- Reads CSV from a Blob endpoint  
- Fully config-driven:
  - endpoint  
  - container  
  - path/prefix  
  - credentials  
- Chunked or bounded reads acceptable for MVP  

### blob_parquet_sink
- Writes Parquet to a Blob endpoint  
- Deterministic file naming  
- Idempotent behavior for MVP  

---

## End-to-End Compose

Provide a top-level Docker Compose stack that brings up:
- Blob source emulator  
- Blob sink emulator  
- Seafarer container  
- Agent runner container  

A single command must execute the full voyage.

---

## Acceptance Criteria

- `docker compose up` completes without manual intervention  
- Parquet output exists in sink emulator  
- Agent runner outputs valid JSON manifests  
- No infra dependencies embedded in the Seafarer image  

---

## Notes

- The sailing metaphor is semantic only  
- JSON schemas must remain stable and machine-readable  
- Prefer determinism and clarity over abstraction
