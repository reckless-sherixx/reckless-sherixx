#!/usr/bin/env python3
"""Prepare a portrait for high-contrast ASCII conversion."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "assets" / "source-portrait.jpg"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "portrait-prepped.png"


def prepare_portrait(
    input_path: Path,
    output_path: Path,
    remove_background: Callable[[Image.Image], Image.Image] | None = None,
) -> tuple[int, int]:
    """Isolate, locally contrast, and composite a portrait onto pure white."""
    if remove_background is None:
        from rembg import remove

        remove_background = remove

    source = Image.open(input_path).convert("RGBA")
    cutout = remove_background(source).convert("RGBA")
    rgb = np.asarray(cutout.convert("RGB"))
    alpha = np.asarray(cutout.getchannel("A"), dtype=np.float32) / 255.0

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    local_contrast = clahe.apply(gray)
    gray = cv2.addWeighted(gray, 0.4, local_contrast, 0.6, 0)
    gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

    feathered = cv2.GaussianBlur(alpha, (0, 0), 1.0)
    mask = np.minimum(feathered, alpha)
    composite = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
    result = Image.fromarray(np.clip(composite, 0, 255).astype(np.uint8), mode="L")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    return result.size


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", default=DEFAULT_INPUT)
    parser.add_argument("output", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    width, height = prepare_portrait(args.input, args.output)
    print(f"wrote {args.output} ({width}x{height})")


if __name__ == "__main__":
    main()
