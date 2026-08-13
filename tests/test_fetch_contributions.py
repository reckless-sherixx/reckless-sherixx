import datetime
import json
from pathlib import Path

import pytest

from scripts.fetch_contributions import build_data, parse_days, write_json_atomic


FIXTURE = Path(__file__).parent / "fixtures" / "contributions.html"


def test_parse_days_reads_dates_and_counts():
    assert parse_days(FIXTURE.read_text(encoding="utf-8")) == [
        {"date": "2026-08-10", "count": 0},
        {"date": "2026-08-11", "count": 2},
        {"date": "2026-08-12", "count": 7},
        {"date": "2026-08-13", "count": 0},
    ]


def test_parse_days_rejects_missing_calendar():
    with pytest.raises(ValueError, match="no contribution calendar cells"):
        parse_days("<html></html>")


def test_build_data_computes_factual_summary():
    data = build_data(
        "reckless-sherixx",
        parse_days(FIXTURE.read_text(encoding="utf-8")),
        datetime.datetime(2026, 8, 13, tzinfo=datetime.timezone.utc),
    )
    assert data["total_contributions"] == 9
    assert data["active_days"] == 2
    assert data["current_streak"]["length"] == 2
    assert data["longest_streak"]["length"] == 2
    assert data["best_day"] == {"date": "2026-08-12", "count": 7}


def test_atomic_write_replaces_valid_json(tmp_path):
    output = tmp_path / "contributions.json"
    output.write_text('{"old": true}', encoding="utf-8")
    write_json_atomic({"username": "reckless-sherixx"}, output)
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "username": "reckless-sherixx"
    }
