#!/usr/bin/env python3
"""Render normalized GitHub contribution data as an animated SVG calendar."""

from __future__ import annotations

import argparse
import datetime
import html
import json
from pathlib import Path


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_WIDTH = 30
TOP_LABEL_HEIGHT = 20
TITLEBAR_HEIGHT = 30

BACKGROUND = "#0a0e14"
BACKGROUND_TOP = "#0d1420"
FRAME = "#238636"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#39d353"
GOLD = "#f2cc60"


def level_for(count: int) -> int:
    """Map a contribution count onto the six-color palette."""
    if count <= 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(
    days: list[dict[str, str | int]],
) -> list[list[dict[str, str | int] | None]]:
    """Lay ordered days into Sunday-first, seven-row week columns."""
    if not days:
        raise ValueError("contribution data is empty")

    ordered = sorted(days, key=lambda day: str(day["date"]))
    first = datetime.date.fromisoformat(str(ordered[0]["date"]))
    lead_padding = (first.weekday() + 1) % 7
    column: list[dict[str, str | int] | None] = [None] * lead_padding
    grid: list[list[dict[str, str | int] | None]] = []

    for day in ordered:
        date = datetime.date.fromisoformat(str(day["date"]))
        weekday = (date.weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        cell = {
            "date": date.isoformat(),
            "count": int(day["count"]),
            "level": level_for(int(day["count"])),
        }
        column.append(cell)
        if len(column) == 7:
            grid.append(column)
            column = []

    if column:
        column.extend([None] * (7 - len(column)))
        grid.append(column)
    return grid


def _month_labels(
    grid: list[list[dict[str, str | int] | None]],
) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    seen: set[tuple[int, int]] = set()
    for column_index, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(str(cell["date"]))
            key = (date.year, date.month)
            if date.day <= 7 and key not in seen:
                labels.append((column_index, date.strftime("%b")))
                seen.add(key)
            break
    return labels


def render_heatmap(data: dict[str, object], static: bool = False) -> str:
    """Return a self-contained GitHub-safe contribution heatmap SVG."""
    username = html.escape(str(data["username"]))
    grid = build_grid(data["days"])
    columns = len(grid)
    art_width = columns * STEP
    art_height = 7 * STEP
    canvas_width = PAD + LEFT_LABEL_WIDTH + art_width + PAD
    stats_height = 88
    canvas_height = TITLEBAR_HEIGHT + TOP_LABEL_HEIGHT + art_height + stats_height + PAD

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" '
            f'height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        )
    ]
    parts.append(
        f"<title>{username} GitHub contribution heatmap</title>"
        f"<desc>{int(data['total_contributions']):,} contributions in the last year</desc>"
    )
    if not static:
        parts.append(
            "<style>@keyframes reveal{0%{opacity:0;transform:translateY(-6px)}"
            "100%{opacity:1;transform:translateY(0)}}"
            ".cell{opacity:0;animation:reveal .42s cubic-bezier(.2,.8,.2,1) both}</style>"
        )
    parts.extend(
        [
            '<defs><linearGradient id="background" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
            f'<stop offset="1" stop-color="{BACKGROUND}"/>'
            "</linearGradient></defs>",
            f'<rect width="{canvas_width}" height="{canvas_height}" rx="12" fill="url(#background)"/>',
            (
                f'<rect x="0.5" y="0.5" width="{canvas_width - 1}" height="{canvas_height - 1}" '
                f'rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.65"/>'
            ),
            (
                f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{canvas_width}" y2="{TITLEBAR_HEIGHT}" '
                f'stroke="{FRAME}" stroke-opacity="0.35"/>'
            ),
        ]
    )
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(
            f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR_HEIGHT / 2}" r="5" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{canvas_width / 2}" y="{TITLEBAR_HEIGHT / 2 + 4}" fill="{MUTED}" '
        f'font-size="12" text-anchor="middle">{username}@github: ~/contributions --graph</text>'
    )

    grid_top = TITLEBAR_HEIGHT + TOP_LABEL_HEIGHT
    grid_left = PAD + LEFT_LABEL_WIDTH
    for column_index, label in _month_labels(grid):
        parts.append(
            f'<text x="{grid_left + column_index * STEP}" y="{TITLEBAR_HEIGHT + 14}" '
            f'fill="{MUTED}" font-size="10">{label}</text>'
        )
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = grid_top + row * STEP + CELL * 0.78
        parts.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{label}</text>')

    for column_index, column in enumerate(grid):
        x = grid_left + column_index * STEP
        for row_index, cell in enumerate(column):
            if cell is None:
                continue
            y = grid_top + row_index * STEP
            count = int(cell["count"])
            date_text = html.escape(str(cell["date"]))
            plural = "" if count == 1 else "s"
            animation = ""
            if not static:
                delay = column_index * 0.018 + row_index * 0.045
                animation = f' class="cell" style="animation-delay:{delay:.3f}s"'
            parts.append(
                f'<rect{animation} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[int(cell["level"])]}"><title>{date_text}: {count} contribution{plural}'
                "</title></rect>"
            )

    legend_y = grid_top + art_height + 6
    legend_x = canvas_width - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(
        f'<text x="{legend_x}" y="{legend_y + CELL * 0.8:.1f}" fill="{MUTED}" '
        'font-size="10" text-anchor="end">Less</text>'
    )
    box_x = legend_x + 8
    for color in PALETTE:
        parts.append(
            f'<rect x="{box_x}" y="{legend_y}" width="{CELL - 1}" height="{CELL - 1}" '
            f'rx="2.2" fill="{color}"/>'
        )
        box_x += CELL
    parts.append(
        f'<text x="{box_x + 4}" y="{legend_y + CELL * 0.8:.1f}" fill="{MUTED}" '
        'font-size="10">More</text>'
    )

    separator_y = legend_y + CELL + 14
    parts.append(
        f'<line x1="0" y1="{separator_y}" x2="{canvas_width}" y2="{separator_y}" '
        f'stroke="{FRAME}" stroke-opacity="0.25"/>'
    )
    total = int(data["total_contributions"])
    current = int(data["current_streak"]["length"])
    longest = int(data["longest_streak"]["length"])
    best = data["best_day"]
    date_range = data["range"]
    line_y = separator_y + 24
    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{ACCENT}"><tspan '
        f'font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year'
        "</tspan></text>"
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{line_y}" font-size="12" fill="{MUTED}" '
        f'text-anchor="end">{html.escape(str(date_range["start"]))} → '
        f'{html.escape(str(date_range["end"]))}</text>'
    )
    line_y += 24
    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{MUTED}">current streak '
        f'<tspan fill="{TEXT}" font-weight="700">{current} days</tspan><tspan> · longest </tspan>'
        f'<tspan fill="{TEXT}" font-weight="700">{longest} days</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{line_y}" font-size="12" fill="{MUTED}" '
        f'text-anchor="end">best day <tspan fill="{GOLD}" font-weight="700">{int(best["count"])}</tspan> '
        f'on {html.escape(str(best["date"]))}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def write_svg_atomic(svg: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--static", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    svg = render_heatmap(data, static=args.static)
    write_svg_atomic(svg, args.output)
    print(f"wrote {args.output} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
