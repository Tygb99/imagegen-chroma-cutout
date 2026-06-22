from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import re
import shutil


def die(message: str) -> None:
    raise SystemExit(f"Error: {message}")


def normalize_prefix(raw: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", raw.strip()).strip("-._").lower()
    return normalized or datetime.now().strftime("designhub-upload-%Y%m%d-%H%M")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy PNG assets to DesignHub-safe unique basenames and write a matching CSV."
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--images-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--digits", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    return parser


def run(args: argparse.Namespace) -> None:
    metadata_path = Path(args.csv)
    images_dir = Path(args.images_dir)
    out_dir = Path(args.out_dir)
    out_csv = Path(args.out_csv)

    if not metadata_path.exists():
        die(f"CSV not found: {metadata_path}")
    if not images_dir.is_dir():
        die(f"Images directory not found: {images_dir}")
    if args.start < 1:
        die("--start must be 1 or greater")
    if args.digits < 2:
        die("--digits must be 2 or greater")
    if out_csv.exists() and not args.force:
        die(f"Output CSV already exists: {out_csv}")

    with metadata_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames or "fileName" not in fieldnames:
        die("CSV must include a fileName column")
    if not rows:
        die("CSV has no rows")

    source_names = [row["fileName"] for row in rows]
    repeated_sources = sorted({name for name in source_names if source_names.count(name) > 1})
    if repeated_sources:
        die(f"Input CSV has duplicate fileName values: {', '.join(repeated_sources)}")

    prefix = normalize_prefix(args.prefix)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    output_rows = []
    output_names = []
    for offset, row in enumerate(rows):
        source_base = row["fileName"]
        source_png = images_dir / f"{source_base}.png"
        if not source_png.exists():
            die(f"Missing PNG for CSV row: {source_png}")

        next_index = args.start + offset
        new_base = f"{prefix}-{next_index:0{args.digits}d}"
        destination = out_dir / f"{new_base}.png"
        if destination.exists() and not args.force:
            die(f"Output PNG already exists: {destination}")

        shutil.copy2(source_png, destination)
        next_row = dict(row)
        next_row["fileName"] = new_base
        output_rows.append(next_row)
        output_names.append(new_base)

    repeated_outputs = sorted({name for name in output_names if output_names.count(name) > 1})
    if repeated_outputs:
        die(f"Generated duplicate output names: {', '.join(repeated_outputs)}")

    with out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"PNG dir: {out_dir}")
    print(f"CSV: {out_csv}")
    print(f"Rows: {len(output_rows)}")
    print(f"First fileName: {output_rows[0]['fileName']}")
    print(f"Last fileName: {output_rows[-1]['fileName']}")


def main() -> None:
    args = build_parser().parse_args()
    run(args)

