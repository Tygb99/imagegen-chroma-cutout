from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import numpy as np


Color = tuple[int, int, int]
DESCRIPTION = "Remove a flat chroma-key background and write an alpha image."


def die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_pillow():
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        die("Pillow is required. Install dependencies with `python3 -m pip install -r requirements.txt`.")
    return Image, ImageFilter


def parse_color(value: str) -> Color:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", value.strip())
    if not match:
        die("--key-color must be a hex RGB value such as #00ff00.")
    raw = match.group(1)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def smoothstep(values):
    clipped = np.clip(values, 0.0, 1.0)
    return clipped * clipped * (3.0 - 2.0 * clipped)


def sample_key(data, mode: str, fallback: Color) -> Color:
    if mode == "none":
        return fallback
    if mode == "corners":
        height, width = data.shape[:2]
        samples = np.array(
            [
                data[0, 0, :3],
                data[0, width - 1, :3],
                data[height - 1, 0, :3],
                data[height - 1, width - 1, :3],
            ],
            dtype=np.uint8,
        )
    else:
        rgb = data[:, :, :3]
        samples = np.concatenate([rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]], axis=0)
    red, green, blue = np.rint(np.median(samples.astype(np.int16), axis=0)).astype(np.uint8)
    return int(red), int(green), int(blue)


def spill_channels(key: Color) -> list[int]:
    key_max = max(key)
    if key_max < 128:
        return []
    return [index for index, value in enumerate(key) if value >= key_max - 16 and value >= 128]


def remove_background(args: argparse.Namespace) -> None:
    Image, ImageFilter = load_pillow()
    source = Path(args.input)
    output = Path(args.out)

    if not source.exists():
        die(f"Input image not found: {source}")
    if output.exists() and not args.force:
        die(f"Output already exists: {output}. Use --force to overwrite.")
    if output.suffix.lower() not in {".png", ".webp"}:
        die("--out must end in .png or .webp to preserve alpha.")
    if args.soft_matte and args.transparent_threshold >= args.opaque_threshold:
        die("--transparent-threshold must be lower than --opaque-threshold.")

    source_image = Image.open(source).convert("RGBA")
    data = np.array(source_image, dtype=np.uint8)
    rgb = data[:, :, :3].astype(np.int16)
    source_alpha = data[:, :, 3].astype(np.float32)
    key = sample_key(data, args.auto_key, parse_color(args.key_color))
    key_array = np.array(key, dtype=np.int16)
    distance = np.max(np.abs(rgb - key_array), axis=2)
    key_like = distance <= (args.opaque_threshold if args.soft_matte else args.tolerance)

    if args.soft_matte:
        ratio = (distance.astype(np.float32) - float(args.transparent_threshold)) / (
            float(args.opaque_threshold) - float(args.transparent_threshold)
        )
        matte = np.rint(255.0 * smoothstep(ratio)).astype(np.uint8)
    else:
        matte = np.where(distance <= args.tolerance, 0, 255).astype(np.uint8)

    next_alpha = np.rint(matte.astype(np.float32) * (source_alpha / 255.0)).astype(np.uint8)
    next_alpha[next_alpha <= 8] = 0
    image_data = data.copy()
    transparent_mask = key_like & (next_alpha == 0)
    partial_mask = key_like & (next_alpha > 0) & (next_alpha < 255)
    image_data[transparent_mask] = (0, 0, 0, 0)
    image_data[partial_mask, 3] = next_alpha[partial_mask]

    if args.despill or args.spill_cleanup:
        spill = np.array(spill_channels(key), dtype=np.int64)
        if spill.size:
            keep = np.array([index for index in range(3) if index not in set(spill.tolist())])
            if keep.size:
                anchor = image_data[:, :, keep].max(axis=2).astype(np.int16)
                cap = np.maximum(0, anchor - 1)
                cleanup = key_like & (image_data[:, :, 3] < 252) & (image_data[:, :, 3] > 0)
                for channel in spill:
                    values = image_data[:, :, int(channel)].astype(np.int16)
                    values[cleanup] = np.minimum(values[cleanup], cap[cleanup])
                    image_data[:, :, int(channel)] = values.astype(np.uint8)

    transparent = int(np.count_nonzero(transparent_mask))
    partial = int(np.count_nonzero(partial_mask))
    image = Image.fromarray(image_data)

    if args.edge_contract:
        alpha = image.getchannel("A")
        for _ in range(args.edge_contract):
            alpha = alpha.filter(ImageFilter.MinFilter(3))
        image.putalpha(alpha)

    if args.edge_feather:
        alpha = image.getchannel("A").filter(ImageFilter.GaussianBlur(args.edge_feather))
        image.putalpha(alpha)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"Wrote {output}")
    print(f"Key color: #{key[0]:02x}{key[1]:02x}{key[2]:02x}")
    print(f"Transparent pixels: {transparent}")
    print(f"Partially transparent pixels: {partial}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--key-color", default="#00ff00")
    parser.add_argument("--tolerance", type=int, default=48)
    parser.add_argument("--auto-key", choices=["none", "corners", "border"], default="border")
    parser.add_argument("--soft-matte", action="store_true")
    parser.add_argument("--transparent-threshold", type=int, default=12)
    parser.add_argument("--opaque-threshold", type=int, default=220)
    parser.add_argument("--edge-feather", type=float, default=0)
    parser.add_argument("--edge-contract", type=int, default=0)
    parser.add_argument("--spill-cleanup", action="store_true")
    parser.add_argument("--despill", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    remove_background(args)

