#!/usr/bin/env python3
"""Fetch and normalize the public GitHub contribution calendar."""

from __future__ import annotations

import argparse
import datetime
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


DEFAULT_USERNAME = "reckless-sherixx"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"
USER_AGENT = "reckless-sherixx-profile-readme/1.0"


def fetch_contribution_html(
    username: str,
    *,
    get: Callable[..., Any] = requests.get,
) -> str:
    """Return GitHub's public contribution-calendar fragment for *username*."""
    url = f"https://github.com/users/{username}/contributions"
    response = get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return response.text


def parse_days(html_text: str) -> list[dict[str, str | int]]:
    """Parse dated contribution cells and their tooltip counts."""
    soup = BeautifulSoup(html_text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        raise ValueError("no contribution calendar cells found")

    days: list[dict[str, str | int]] = []
    for cell in cells:
        tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
        text = tooltip.get_text(" ", strip=True) if tooltip else ""
        match = re.match(r"([0-9,]+) contributions?", text, re.IGNORECASE)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": str(cell["data-date"]), "count": count})

    return sorted(days, key=lambda day: str(day["date"]))


def _current_streak(days: list[dict[str, str | int]]) -> dict[str, object]:
    index = len(days) - 1
    if int(days[index]["count"]) == 0:
        index -= 1

    end_index = index
    while index >= 0 and int(days[index]["count"]) > 0:
        index -= 1

    length = end_index - index
    if length == 0:
        return {"length": 0, "start": None, "end": None}
    return {
        "length": length,
        "start": days[index + 1]["date"],
        "end": days[end_index]["date"],
    }


def _longest_streak(days: list[dict[str, str | int]]) -> dict[str, object]:
    best_length = 0
    best_start: str | None = None
    best_end: str | None = None
    run_length = 0
    run_start: str | None = None

    for day in days:
        if int(day["count"]) > 0:
            if run_length == 0:
                run_start = str(day["date"])
            run_length += 1
            if run_length > best_length:
                best_length = run_length
                best_start = run_start
                best_end = str(day["date"])
        else:
            run_length = 0
            run_start = None

    return {"length": best_length, "start": best_start, "end": best_end}


def build_data(
    username: str,
    days: list[dict[str, str | int]],
    generated_at: datetime.datetime | None = None,
) -> dict[str, object]:
    """Validate normalized days and derive display statistics."""
    if not days:
        raise ValueError("contribution data is empty")

    ordered = sorted(days, key=lambda day: str(day["date"]))
    dates = [str(day["date"]) for day in ordered]
    if len(dates) != len(set(dates)):
        raise ValueError("contribution dates must be unique")
    for date_text in dates:
        datetime.date.fromisoformat(date_text)

    total = sum(int(day["count"]) for day in ordered)
    active_days = sum(int(day["count"]) > 0 for day in ordered)
    best = max(ordered, key=lambda day: int(day["count"]))

    monthly: dict[str, int] = {}
    for day in ordered:
        month = str(day["date"])[:7]
        monthly[month] = monthly.get(month, 0) + int(day["count"])

    timestamp = generated_at or datetime.datetime.now(datetime.timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
    generated = timestamp.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "username": username,
        "generated_at": generated,
        "range": {"start": dates[0], "end": dates[-1]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": _current_streak(ordered),
        "longest_streak": _longest_streak(ordered),
        "best_day": {"date": best["date"], "count": int(best["count"])},
        "monthly": [
            {"month": month, "total": value}
            for month, value in sorted(monthly.items())
        ],
        "days": ordered,
    }


def write_json_atomic(data: dict[str, object], output_path: Path) -> None:
    """Replace *output_path* only after a complete JSON payload is ready."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2) + "\n"
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    html_text = fetch_contribution_html(args.username)
    data = build_data(args.username, parse_days(html_text))
    write_json_atomic(data, args.output)
    print(
        f"wrote {args.output}: {data['total_contributions']} contributions "
        f"from {data['range']['start']} to {data['range']['end']}"
    )


if __name__ == "__main__":
    main()
