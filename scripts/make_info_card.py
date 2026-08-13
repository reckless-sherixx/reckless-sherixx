#!/usr/bin/env python3
"""Generate the static-content neofetch-style identity card."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "info-card.svg"
ROWS = (
    ("Name", "Vidyansh Singh"),
    ("Role", "Open Source Developer · Kubernetes · Go"),
    ("Focus", "Cloud Native and Distributed Systems"),
    ("Stack", "Go · Kubernetes · TypeScript · Docker"),
    ("GitHub", "github.com/reckless-sherixx"),
)

WIDTH = 980
HEIGHT = 754
BACKGROUND = "#0a0e14"
BACKGROUND_TOP = "#0d1420"
FRAME = "#238636"
MUTED = "#7d8590"
TEXT = "#e6edf3"
GREEN = "#39d353"
CYAN = "#22d3ee"


def render_info_card(static: bool = False) -> str:
    """Return a self-contained identity-card SVG."""
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        ),
        "<title>Vidyansh Singh profile information</title>",
        (
            "<desc>Open Source Developer specializing in Kubernetes and Go, focused on "
            "Cloud Native and Distributed Systems.</desc>"
        ),
    ]
    if not static:
        parts.append(
            "<style>@keyframes lineIn{0%{opacity:0;transform:translateX(-18px)}"
            "100%{opacity:1;transform:translateX(0)}}"
            ".line{opacity:0;animation:lineIn .48s cubic-bezier(.2,.8,.2,1) both}</style>"
        )
    parts.extend(
        [
            '<defs><linearGradient id="cardBackground" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
            f'<stop offset="1" stop-color="{BACKGROUND}"/>'
            "</linearGradient></defs>",
            f'<rect width="{WIDTH}" height="{HEIGHT}" rx="24" fill="url(#cardBackground)"/>',
            (
                f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="24" '
                f'fill="none" stroke="{FRAME}" stroke-opacity="0.65" stroke-width="2"/>'
            ),
            f'<line x1="0" y1="60" x2="{WIDTH}" y2="60" stroke="{FRAME}" stroke-opacity="0.35"/>',
        ]
    )
    for index, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{42 + index * 32}" cy="30" r="10" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH / 2}" y="39" fill="{MUTED}" font-size="22" '
        'text-anchor="middle">reckless-sherixx@github: ~$ neofetch</text>'
    )

    content_class = "" if static else ' class="line" style="animation-delay:.10s"'
    parts.append(
        f'<g{content_class}><text x="64" y="134" fill="{GREEN}" font-size="34" '
        'font-weight="700">vidyansh@github</text>'
        f'<line x1="64" y1="154" x2="916" y2="154" stroke="{FRAME}" stroke-width="2"/>'
        "</g>"
    )

    start_y = 224
    row_gap = 88
    for index, (key, value) in enumerate(ROWS):
        delay = 0.25 + index * 0.14
        attributes = "" if static else f' class="line" style="animation-delay:{delay:.2f}s"'
        y = start_y + index * row_gap
        parts.append(
            f'<g{attributes}><text x="64" y="{y}" fill="{CYAN}" font-size="25" '
            f'font-weight="700">{html.escape(key)}</text>'
            f'<text x="244" y="{y}" fill="{TEXT}" font-size="25">{html.escape(value)}</text></g>'
        )

    footer_attributes = "" if static else ' class="line" style="animation-delay:1.05s"'
    parts.append(
        f'<g{footer_attributes}><line x1="64" y1="684" x2="916" y2="684" '
        f'stroke="{FRAME}" stroke-opacity="0.45"/>'
        f'<text x="64" y="724" fill="{MUTED}" font-size="21">$ '
        f'<tspan fill="{GREEN}">building in public</tspan>'
        f'<tspan fill="{TEXT}">_</tspan></text></g>'
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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--static", action="store_true")
    args = parser.parse_args()

    svg = render_info_card(static=args.static)
    write_svg(svg, args.output)
    print(f"wrote {args.output} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
