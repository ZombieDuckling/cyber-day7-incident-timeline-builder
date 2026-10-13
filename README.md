# Cyber Day 7: Incident timeline builder (Python)

This is a very basic, beginner-friendly cybersecurity portfolio project.
It reads timestamped security events from JSON or CSV, sorts them, and prints
an incident timeline.

## Legal and ethical use

Use this only on logs you are authorized to analyze. This project is for
defensive security learning and incident response practice.

## Workflow

### 1) Research (quick references)

1. NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide  
   https://csrc.nist.gov/pubs/sp/800/61/r2/final
2. Plaso log2timeline user docs (timeline extraction workflow)  
   https://plaso.readthedocs.io/en/latest/sources/user/Using-log2timeline.html
3. Python standard library docs (`datetime`, `csv`)  
   https://docs.python.org/3/library/datetime.html  
   https://docs.python.org/3/library/csv.html

### 2) Learn (key points applied)

- Timelines help incident responders reconstruct what happened and in what
  order, which supports containment and recovery decisions (NIST).
- A practical timeline process is: collect events from multiple sources,
  normalize key fields, then sort chronologically (Plaso/log2timeline concept).
- Use Python built-ins (`csv.DictReader`, JSON, and `datetime`) to keep the
  project lightweight and easy to understand.

### 3) Execute (implementation)

- `timeline_builder.py`
  - Accepts `.json` or `.csv` input.
  - Detects common timestamp field names.
  - Parses ISO 8601 timestamps (including `Z`).
  - Treats timezone-naive fallback timestamps as UTC so mixed timestamp styles
    sort safely.
  - Sorts events by timestamp.
  - Prints timeline to terminal or writes to a file via `--output`.
- `tests/test_timeline_builder.py`
  - Characterizes JSON/CSV loading, timestamp parsing, sorting, rendering, and
    CLI output behavior.
- `.github/workflows/ci.yml`
  - Runs the pytest suite on Python 3.10 and 3.12 for PRs and main pushes.
- Sample input files:
  - `sample_events.json`
  - `sample_events.csv`

### 4) Push

If GitHub CLI (`gh`) is authenticated, publish this project as:
`ZombieDuckling/cyber-day7-incident-timeline-builder`.

## How to run

From this folder:

```bash
python3 timeline_builder.py sample_events.json
python3 timeline_builder.py sample_events.csv
python3 timeline_builder.py sample_events.json --output timeline.txt
```

## How to test

This project has no runtime dependencies. The test suite uses `pytest`:

```bash
python3 -m pip install pytest
python3 -m pytest -q
```

## Example output

```text
timestamp | source | event
------------------------------------------------------------------------
2026-03-16T06:35:00+00:00 | auth | 5 failed SSH logins for user admin
2026-03-16T06:40:00+00:00 | firewall | Inbound scan from 203.0.113.25
2026-03-16T06:52:00+00:00 | endpoint | Suspicious process blocked by EDR
```
