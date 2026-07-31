from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import timezone
from pathlib import Path

import pytest

from timeline_builder import (
    build_timeline,
    detect_timestamp_key,
    load_events,
    parse_timestamp,
    render_timeline,
)


def test_parse_timestamp_accepts_zulu_and_marks_naive_as_utc() -> None:
    assert parse_timestamp("2026-03-16T06:35:00Z").tzinfo is not None
    naive = parse_timestamp("2026-03-16 06:35:00")
    assert naive.tzinfo is timezone.utc
    assert naive.isoformat() == "2026-03-16T06:35:00+00:00"


def test_detect_timestamp_key_accepts_common_names() -> None:
    assert detect_timestamp_key({"event_time": "2026-03-16T06:35:00Z"}) == "event_time"


def test_detect_timestamp_key_reports_supported_names() -> None:
    with pytest.raises(KeyError, match="timestamp, time, datetime, event_time, date"):
        detect_timestamp_key({"message": "no timestamp here"})


def test_build_timeline_sorts_events_and_handles_action_fallback() -> None:
    events = [
        {"timestamp": "2026-03-16T06:52:00Z", "source": "endpoint", "action": "EDR blocked process"},
        {"time": "2026-03-16 06:35:00", "source": "auth", "event": "Failed SSH logins"},
    ]

    timeline = build_timeline(events)

    assert [item["source"] for item in timeline] == ["auth", "endpoint"]
    assert timeline[1]["event"] == "EDR blocked process"


def test_render_timeline_matches_documented_shape() -> None:
    timeline = build_timeline(
        [
            {"timestamp": "2026-03-16T06:40:00Z", "source": "firewall", "event": "Inbound scan"},
            {"timestamp": "2026-03-16T06:35:00Z", "source": "auth", "event": "Failed SSH logins"},
        ]
    )

    rendered = render_timeline(timeline)

    assert rendered.splitlines()[0] == "timestamp | source | event"
    assert "2026-03-16T06:35:00+00:00 | auth | Failed SSH logins" in rendered
    assert rendered.index("auth") < rendered.index("firewall")


def test_load_events_from_json_and_csv(tmp_path: Path) -> None:
    json_path = tmp_path / "events.json"
    json_path.write_text(json.dumps([{"timestamp": "2026-03-16T06:35:00Z"}]), encoding="utf-8")

    csv_path = tmp_path / "events.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "source", "event"])
        writer.writeheader()
        writer.writerow({"timestamp": "2026-03-16T06:35:00Z", "source": "auth", "event": "Failed SSH"})

    assert load_events(json_path) == [{"timestamp": "2026-03-16T06:35:00Z"}]
    assert load_events(csv_path)[0]["source"] == "auth"


def test_load_events_rejects_non_list_json(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(json.dumps({"timestamp": "2026-03-16T06:35:00Z"}), encoding="utf-8")

    with pytest.raises(ValueError, match="JSON input must be a list of objects"):
        load_events(path)


def test_cli_writes_sorted_timeline(tmp_path: Path) -> None:
    input_path = tmp_path / "events.json"
    output_path = tmp_path / "timeline.txt"
    input_path.write_text(
        json.dumps(
            [
                {"timestamp": "2026-03-16T06:40:00Z", "source": "firewall", "event": "Inbound scan"},
                {"timestamp": "2026-03-16T06:35:00Z", "source": "auth", "event": "Failed SSH"},
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "timeline_builder.py", str(input_path), "--output", str(output_path)],
        check=True,
        text=True,
        capture_output=True,
    )

    assert f"Timeline written to {output_path}" in result.stdout
    written = output_path.read_text(encoding="utf-8")
    assert written.index("auth") < written.index("firewall")
