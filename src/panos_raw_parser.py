"""PanOS raw log parser - parses key=value style logs (CEF/ArcSight format)."""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from tabulate import tabulate

# Human-readable labels for known keys
LABELS = {
    "eventId": "Event ID",
    "externalId": "External ID",
    "start": "Start Time",
    "end": "End Time",
    "art": "Agent Receipt Time",
    "rt": "Receipt Time",
    "app": "Application",
    "proto": "Protocol",
    "src": "Source IP",
    "dst": "Destination IP",
    "spt": "Source Port",
    "dpt": "Destination Port",
    "act": "Action",
    "cat": "Category",
    "catdt": "Category Device Type",
    "request": "Request URL",
    "requestMethod": "HTTP Method",
    "requestContext": "Content Type",
    "requestClientApplication": "User Agent",
    "ahost": "Agent Host",
    "agt": "Agent IP",
    "amac": "Agent MAC",
    "av": "Agent Version",
    "dvchost": "Device Host",
    "deviceSeverity": "Severity",
}

# Timestamp keys (Unix ms)
TIMESTAMP_KEYS = {"start", "end", "art", "rt"}

# Split at: space followed by key= (values can contain spaces)
PARSE_RE = re.compile(r" (?=[\w.]+=)")


def parse_line(line: str) -> dict[str, str]:
    """Parse a single PanOS/CEF-style key=value log line into a dict."""
    line = line.strip()
    if not line:
        return {}
    result = {}
    for pair in PARSE_RE.split(line):
        if "=" in pair:
            key, _, value = pair.partition("=")
            result[key] = value
    return result


def parse(raw: str) -> list[dict[str, str]]:
    """Parse raw log data. Handles single or multiple lines."""
    events = []
    for line in raw.strip().splitlines():
        parsed = parse_line(line)
        if parsed:
            events.append(parsed)
    return events


def fmt_timestamp(ms_str: str) -> str:
    """Convert Unix ms timestamp to verbose readable format."""
    try:
        ts = int(ms_str)
        dt = datetime.utcfromtimestamp(ts / 1000)
        return dt.strftime("%A, %B %d, %Y at %I:%M:%S %p UTC")
    except (ValueError, OSError):
        return ms_str


def fmt_value(key: str, value: str) -> str:
    """Format value for display."""
    if not value:
        return ""
    if key in TIMESTAMP_KEYS and value.isdigit():
        return fmt_timestamp(value)
    if key == "deviceSeverity" and value.isdigit():
        sev = int(value)
        return f"{value} ({'Low' if sev <= 2 else 'Medium' if sev <= 4 else 'High' if sev <= 6 else 'Critical'})"
    return value


def label(key: str) -> str:
    return LABELS.get(key, key.replace(".", " ").replace("_", " ").title())


def to_table(events: list[dict[str, str]], skip_empty: bool = True) -> str:
    """Format parsed events as tabulate output."""
    if not events:
        return "No log entries parsed."
    if len(events) == 1:
        rows = []
        for key, value in events[0].items():
            display_value = fmt_value(key, value)
            if skip_empty and not display_value:
                continue
            rows.append((label(key), display_value))
        return tabulate(rows, headers=["Field", "Value"], tablefmt="rounded_grid")

    # Multiple events: show each as a section
    parts = []
    for i, evt in enumerate(events):
        rows = [(label(k), fmt_value(k, v)) for k, v in evt.items() if not skip_empty or fmt_value(k, v)]
        parts.append(f"\n--- Log entry {i + 1} ---\n" + tabulate(rows, headers=["Field", "Value"], tablefmt="rounded_grid"))
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse PanOS raw log data (key=value format)")
    parser.add_argument("input", nargs="?", help="File path or '-' for stdin (default: stdin)")
    parser.add_argument("-f", "--file", dest="file", help="Read from file")
    parser.add_argument("-s", "--show-empty", action="store_true", help="Show fields with empty values")
    parser.add_argument("-r", "--raw", action="store_true", help="Output raw dict (key=value) instead of table")
    args = parser.parse_args()

    # Get input
    raw_text: str
    if args.file:
        raw_text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    elif args.input and args.input != "-":
        raw_text = Path(args.input).read_text(encoding="utf-8", errors="replace")
    else:
        raw_text = sys.stdin.read()

    events = parse(raw_text)
    if not events:
        print("No log entries parsed.", file=sys.stderr)
        sys.exit(1)

    if args.raw:
        for evt in events:
            for k, v in evt.items():
                print(f"{k}={v}")
            if len(events) > 1:
                print("---")
    else:
        print(to_table(events, skip_empty=not args.show_empty))


if __name__ == "__main__":
    main()
