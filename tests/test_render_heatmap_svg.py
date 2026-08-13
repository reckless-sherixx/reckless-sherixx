import datetime
import xml.etree.ElementTree as ET

from scripts.fetch_contributions import build_data
from scripts.render_heatmap_svg import build_grid, level_for, render_heatmap


DAYS = [
    {"date": "2026-08-09", "count": 0},
    {"date": "2026-08-10", "count": 1},
    {"date": "2026-08-11", "count": 6},
]


def test_level_for_has_six_bounded_levels():
    assert [level_for(value) for value in (0, 1, 6, 16, 31, 51)] == [0, 1, 2, 3, 4, 5]


def test_build_grid_starts_on_sunday():
    grid = build_grid(DAYS)
    assert grid[0][0]["date"] == "2026-08-09"
    assert grid[0][2]["count"] == 6


def test_render_heatmap_is_valid_accessible_svg():
    data = build_data(
        "reckless-sherixx",
        DAYS,
        datetime.datetime(2026, 8, 13, tzinfo=datetime.timezone.utc),
    )
    svg = render_heatmap(data)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "reckless-sherixx@github" in svg
    assert "7 contributions in the last year" in svg
    assert "@keyframes reveal" in svg
    assert "repeatCount=\"indefinite\"" not in svg
    assert "2026-08-11: 6 contributions" in svg


def test_static_render_contains_no_animation():
    data = build_data("reckless-sherixx", DAYS)
    assert "@keyframes" not in render_heatmap(data, static=True)
