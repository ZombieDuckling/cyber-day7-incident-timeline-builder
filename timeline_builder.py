#!/usr/bin/env python3
"""Very basic incident timeline builder.

Reads timestamped events from JSON or CSV and prints a sorted timeline.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

TIMESTAMP_FIELDS = ["timestamp", "time", "datetime", "event_time", "date"]


def parse_timestamp(raw: str) -> datetime:
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    # Try ISO-8601 first
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    # A couple of beginner-friendly fallback formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported timestamp format: {raw}")


def detect_timestamp_key(record: dict[str, Any]) -> str:
    for key in TIMESTAMP_FIELDS:
        if key in record:
            return key
    raise KeyError(f"No timestamp field found. Tried: {', '.join(TIMESTAMP_FIELDS)}")


def load_events(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of objects")
        return data

    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    raise ValueError("Unsupported file type. Use .json or .csv")


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    timestamp_key = detect_timestamp_key(event)
    ts = parse_timestamp(str(event[timestamp_key]))

    return {
        "timestamp": ts,
        "source": event.get("source", "unknown"),
        "event": event.get("event", event.get("action", "(no description)")),
        "raw": event,
    }


def build_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [normalize_event(e) for e in events]
    return sorted(normalized, key=lambda e: e["timestamp"])


def render_timeline(timeline: list[dict[str, Any]]) -> str:
    lines = ["timestamp | source | event", "-" * 72]
    for item in timeline:
        ts = item["timestamp"].isoformat()
        lines.append(f"{ts} | {item['source']} | {item['event']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a sorted incident timeline")
    parser.add_argument("input", type=Path, help="Path to .json or .csv events file")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output file path (if omitted, prints to stdout)",
    )
    args = parser.parse_args()

    events = load_events(args.input)
    timeline = build_timeline(events)
    rendered = render_timeline(timeline)

    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Timeline written to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
