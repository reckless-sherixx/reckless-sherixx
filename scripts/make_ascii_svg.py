#!/usr/bin/env python3
"""Convert a prepared portrait into a one-shot animated ASCII SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "assets" / "portrait-prepped.png"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "portrait-ascii.svg"
RAMP = " .`:-=+*cs#%@"

CELL_WIDTH = 8
CELL_HEIGHT = 15
PAD = 20
TITLEBAR_HEIGHT = 30
STATUS_HEIGHT = 30
BACKGROUND = "#0a0e14"
BACKGROUND_TOP = "#0d1420"
FRAME = "#238636"
MUTED = "#7d8590"
INK = "#c9d1d9"
GREEN = "#39d353"


def image_to_ascii_rows(
    image: Image.Image,
    cols: int = 100,
    rows: int = 53,
) -> list[str]:
    """Sample *image* into a bright-to-sparse ASCII grid."""
    sampled = image.convert("L").resize((cols, rows), Image.Resampling.LANCZOS)
    result: list[str] = []
    for y in range(rows):
        line: list[str] = []
        for x in range(cols):
            luminance = (sampled.getpixel((x, y)) / 255.0) ** 1.18
            if luminance >= 0.80:
                line.append(" ")
            else:
                index = round((1.0 - luminance) * (len(RAMP) - 1))
                line.append(RAMP[max(0, min(index, len(RAMP) - 1))])
        result.append("".join(line))
    return result


def render_ascii_svg(rows: list[str], static: bool = False) -> str:
    """Render ASCII rows inside a terminal frame with nonlooping row wipes."""
    if not rows:
        raise ValueError("ASCII portrait requires at least one row")

    columns = max(len(row) for row in rows)
    normalized = [row.ljust(columns) for row in rows]
    art_width = columns * CELL_WIDTH
    art_height = len(normalized) * CELL_HEIGHT
    canvas_width = art_width + PAD * 2
    canvas_height = TITLEBAR_HEIGHT + art_height + STATUS_HEIGHT + PAD
    art_top = TITLEBAR_HEIGHT + PAD * 0.35
    status_line_y = TITLEBAR_HEIGHT + art_height + PAD * 0.35
    status_y = status_line_y + 19

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" '
            f'height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        ),
        "<title>Animated ASCII portrait of Vidyansh Singh</title>",
        "<desc>A monochrome terminal portrait that types in once from top to bottom.</desc>",
        '<defs><linearGradient id="portraitBackground" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
        f'<stop offset="1" stop-color="{BACKGROUND}"/>'
        "</linearGradient></defs>",
        (
            f'<rect width="{canvas_width}" height="{canvas_height}" rx="12" '
            'fill="url(#portraitBackground)"/>'
        ),
        (
            f'<rect x="0.5" y="0.5" width="{canvas_width - 1}" height="{canvas_height - 1}" '
            f'rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.65"/>'
        ),
        (
            f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{canvas_width}" y2="{TITLEBAR_HEIGHT}" '
            f'stroke="{FRAME}" stroke-opacity="0.35"/>'
        ),
    ]
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(
            f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR_HEIGHT / 2}" r="5" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{canvas_width / 2}" y="{TITLEBAR_HEIGHT / 2 + 4}" fill="{MUTED}" '
        'font-size="12" text-anchor="middle">reckless-sherixx@github: ~$ ./portrait.sh</text>'
    )

    font_size = CELL_HEIGHT * 0.86
    for row_index, line in enumerate(normalized):
        baseline = art_top + row_index * CELL_HEIGHT + CELL_HEIGHT * 0.74
        row_top = art_top + row_index * CELL_HEIGHT
        safe_line = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{baseline:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{art_width}" '
            f'lengthAdjust="spacing">{safe_line}</text>'
        )
        if static:
            parts.append(text)
            continue

        delay = row_index * 0.11
        parts.append(
            f'<clipPath id="row-{row_index}"><rect x="{PAD}" y="{row_top:.1f}" '
            f'height="{CELL_HEIGHT}" width="0"><animate attributeName="width" from="0" '
            f'to="{art_width}" begin="{delay:.3f}s" dur="0.11s" fill="freeze"/>'
            "</rect></clipPath>"
        )
        parts.append(f'<g clip-path="url(#row-{row_index})">{text}</g>')
        parts.append(
            f'<rect y="{row_top + 1:.1f}" width="{CELL_WIDTH}" height="{CELL_HEIGHT - 2}" '
            f'fill="{INK}" opacity="0"><animate attributeName="x" from="{PAD}" '
            f'to="{PAD + art_width}" begin="{delay:.3f}s" dur="0.11s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + 0.11:.3f}s"/></rect>'
        )

    parts.append(
        f'<line x1="0" y1="{status_line_y:.1f}" x2="{canvas_width}" y2="{status_line_y:.1f}" '
        f'stroke="{FRAME}" stroke-opacity="0.35"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">'
        f'reckless-sherixx@github:~$ whoami <tspan fill="{GREEN}">Vidyansh Singh</tspan>'
        f'<tspan fill="{INK}">_</tspan></text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def write_svg(svg: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", default=DEFAULT_INPUT)
    parser.add_argument("output", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    parser.add_argument("--cols", type=int, default=100)
    parser.add_argument("--rows", type=int, default=53)
    parser.add_argument("--static", action="store_true")
    args = parser.parse_args()

    image = Image.open(args.input)
    svg = render_ascii_svg(
        image_to_ascii_rows(image, cols=args.cols, rows=args.rows),
        static=args.static,
    )
    write_svg(svg, args.output)
    print(f"wrote {args.output} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
