from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Final


DESCRIPTION: Final = "Write a Photopea HTML runner for raw alpha PNG finishing."
PLACEHOLDER: Final = "__PHOTOPEA_RUNNER_CONFIG__"
TEMPLATE_PATH: Final = Path(__file__).resolve().parents[2] / "assets" / "photopea_runner.html"


@dataclass(frozen=True)
class RunnerConfig:
    raw_dir: Path
    processed_dir: Path
    out_file: Path
    target_min_pixels: int
    target_max_pixels: int
    target_dpi: int
    force: bool


def die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def default_runner_path(raw_dir: Path) -> Path:
    if raw_dir.name == "raw" and raw_dir.parent.name == "assets":
        return raw_dir.parent.parent / "photopea" / "runner.html"
    return raw_dir / "photopea-runner.html"


def default_processed_dir(raw_dir: Path) -> Path:
    if raw_dir.name == "raw" and raw_dir.parent.name == "assets":
        return raw_dir.parent / "processed"
    return raw_dir / "processed"


def png_names(raw_dir: Path) -> list[str]:
    return sorted(path.name for path in raw_dir.iterdir() if path.is_file() and path.suffix.lower() == ".png")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--raw-dir", required=True, help="Directory containing raw alpha PNG files.")
    parser.add_argument("--processed-dir", help="Directory where Photopea outputs should be saved.")
    parser.add_argument("--out", help="Path for the generated runner.html.")
    parser.add_argument("--target-min-pixels", type=int, default=2500)
    parser.add_argument("--target-max-pixels", type=int, default=9000)
    parser.add_argument("--target-dpi", type=int, default=350)
    parser.add_argument("--force", action="store_true")
    return parser


def parse_config(args: argparse.Namespace) -> RunnerConfig:
    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir) if args.processed_dir else default_processed_dir(raw_dir)
    out_file = Path(args.out) if args.out else default_runner_path(raw_dir)
    return RunnerConfig(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        out_file=out_file,
        target_min_pixels=args.target_min_pixels,
        target_max_pixels=args.target_max_pixels,
        target_dpi=args.target_dpi,
        force=args.force,
    )


def validate_config(config: RunnerConfig) -> list[str]:
    if not config.raw_dir.is_dir():
        die(f"Raw PNG directory not found: {config.raw_dir}")
    if config.target_min_pixels < 1:
        die("--target-min-pixels must be 1 or greater")
    if config.target_max_pixels < config.target_min_pixels:
        die("--target-max-pixels must be greater than or equal to --target-min-pixels")
    if config.target_dpi < 1:
        die("--target-dpi must be 1 or greater")
    if not TEMPLATE_PATH.exists():
        die(f"Runner template not found: {TEMPLATE_PATH}")
    if config.out_file.exists() and not config.force:
        die(f"Output already exists: {config.out_file}. Use --force to overwrite.")
    names = png_names(config.raw_dir)
    if not names:
        die(f"No PNG files found in raw directory: {config.raw_dir}")
    return names


def render_runner(config: RunnerConfig, names: list[str]) -> str:
    payload = {
        "rawDir": str(config.raw_dir),
        "processedDir": str(config.processed_dir),
        "rawFiles": names,
        "targetMinPixels": config.target_min_pixels,
        "targetMaxPixels": config.target_max_pixels,
        "targetDpi": config.target_dpi,
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace(PLACEHOLDER, json.dumps(payload, ensure_ascii=False, indent=2))


def run(config: RunnerConfig) -> None:
    names = validate_config(config)
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.out_file.parent.mkdir(parents=True, exist_ok=True)
    config.out_file.write_text(render_runner(config, names), encoding="utf-8")
    print(f"Runner: {config.out_file}")
    print(f"Raw PNG files: {len(names)}")
    print(f"Processed output folder: {config.processed_dir}")
    print(f"Target: {config.target_min_pixels}-{config.target_max_pixels}px, {config.target_dpi} DPI")


def main() -> None:
    args = build_parser().parse_args()
    run(parse_config(args))
