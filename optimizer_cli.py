#!/usr/bin/env python3
"""
Command-line interface for the Optimizer image toolkit.

Usage examples:
    python optimizer_cli.py jpg input.png output.jpg --quality 85
    python optimizer_cli.py webp input.png output.webp --lossless
    python optimizer_cli.py png input.png output.png --remove-metadata
    python optimizer_cli.py avif input.jpg output.avif --resize 800x600
    python optimizer_cli.py resize input.jpg output.jpg --size 400x300
    python optimizer_cli.py thumbnail input.jpg output.jpg --size 200x200
    python optimizer_cli.py crop input.jpg output.jpg --box 0,0,300,300
    python optimizer_cli.py strip-metadata input.jpg output.jpg
    python optimizer_cli.py batch ./images ./optimized --format webp --quality 75
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from optimizer import Optimizer


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #

def parse_size(value: str) -> tuple[int, int]:
    """Parse 'WIDTHxHEIGHT' into (width, height)."""
    try:
        w, h = value.lower().split("x")
        return (int(w), int(h))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid size '{value}'. Expected format: WIDTHxHEIGHT (e.g. 800x600)"
        ) from exc


def parse_box(value: str) -> tuple[int, int, int, int]:
    """Parse 'LEFT,TOP,RIGHT,BOTTOM' into a 4-tuple."""
    try:
        parts = [int(p.strip()) for p in value.split(",")]
        if len(parts) != 4:
            raise ValueError
        return tuple(parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid box '{value}'. Expected format: LEFT,TOP,RIGHT,BOTTOM (e.g. 0,0,300,300)"
        ) from exc


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def print_result(result: dict[str, Any]) -> None:
    if "error" in result:
        print(f"✗ {result['input_path']} -> error: {result['error']}", file=sys.stderr)
        return

    print(f"✓ {result['input_path']} -> {result['output_path']}")
    if "input_size" in result and "output_size" in result:
        print(
            f"  {human_size(result['input_size'])} -> {human_size(result['output_size'])} "
            f"({result['saved']}% saved) [{result['format']}]"
        )


def print_batch_summary(results: list[dict[str, Any]]) -> None:
    ok = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    for r in results:
        print_result(r)

    print()
    print(f"Total: {len(results)} files | Succeeded: {len(ok)} | Failed: {len(failed)}")

    if ok:
        total_in = sum(r["input_size"] for r in ok)
        total_out = sum(r["output_size"] for r in ok)
        saved_pct = round((1 - total_out / total_in) * 100, 2) if total_in else 0.0
        print(
            f"Total size: {human_size(total_in)} -> {human_size(total_out)} "
            f"({saved_pct}% saved)"
        )


# ---------------------------------------------------------------------- #
# Command handlers
# ---------------------------------------------------------------------- #

def cmd_jpg(args: argparse.Namespace) -> None:
    result = Optimizer.optimize_jpg(
        args.input,
        args.output,
        quality=args.quality,
        optimize=not args.no_optimize,
        progressive=not args.no_progressive,
        remove_metadata=args.remove_metadata,
        resize=args.resize,
    )
    print_result(result)


def cmd_png(args: argparse.Namespace) -> None:
    result = Optimizer.optimize_png(
        args.input,
        args.output,
        optimize=not args.no_optimize,
        compress_level=args.compress_level,
        remove_metadata=args.remove_metadata,
        resize=args.resize,
    )
    print_result(result)


def cmd_webp(args: argparse.Namespace) -> None:
    result = Optimizer.to_webp(
        args.input,
        args.output,
        quality=args.quality,
        method=args.method,
        lossless=args.lossless,
        remove_metadata=args.remove_metadata,
        resize=args.resize,
    )
    print_result(result)


def cmd_avif(args: argparse.Namespace) -> None:
    result = Optimizer.to_avif(
        args.input,
        args.output,
        quality=args.quality,
        remove_metadata=args.remove_metadata,
        resize=args.resize,
    )
    print_result(result)


def cmd_resize(args: argparse.Namespace) -> None:
    result = Optimizer.resize(args.input, args.output, size=args.size)
    print_result(result)


def cmd_thumbnail(args: argparse.Namespace) -> None:
    result = Optimizer.thumbnail(args.input, args.output, size=args.size)
    print_result(result)


def cmd_crop(args: argparse.Namespace) -> None:
    result = Optimizer.crop(args.input, args.output, box=args.box)
    print_result(result)


def cmd_strip_metadata(args: argparse.Namespace) -> None:
    result = Optimizer.remove_metadata(args.input, args.output)
    print_result(result)


def cmd_batch(args: argparse.Namespace) -> None:
    results = Optimizer.batch(
        args.input_folder,
        args.output_folder,
        format=args.format.upper(),
        quality=args.quality,
        remove_metadata=args.remove_metadata,
        resize=args.resize,
    )
    print_batch_summary(results)


# ---------------------------------------------------------------------- #
# Argument parser
# ---------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="optimizer",
        description="Command-line tool for optimizing and converting image formats",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- jpg ---
    p = subparsers.add_parser("jpg", help="Optimize / convert to JPEG")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--quality", type=int, default=80)
    p.add_argument("--no-optimize", action="store_true")
    p.add_argument("--no-progressive", action="store_true")
    p.add_argument("--remove-metadata", action="store_true")
    p.add_argument("--resize", type=parse_size, default=None, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_jpg)

    # --- png ---
    p = subparsers.add_parser("png", help="Optimize / convert to PNG")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--no-optimize", action="store_true")
    p.add_argument("--compress-level", type=int, default=9)
    p.add_argument("--remove-metadata", action="store_true")
    p.add_argument("--resize", type=parse_size, default=None, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_png)

    # --- webp ---
    p = subparsers.add_parser("webp", help="Convert to WEBP")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--quality", type=int, default=80)
    p.add_argument("--method", type=int, default=6)
    p.add_argument("--lossless", action="store_true")
    p.add_argument("--remove-metadata", action="store_true")
    p.add_argument("--resize", type=parse_size, default=None, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_webp)

    # --- avif ---
    p = subparsers.add_parser("avif", help="Convert to AVIF")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--quality", type=int, default=80)
    p.add_argument("--remove-metadata", action="store_true")
    p.add_argument("--resize", type=parse_size, default=None, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_avif)

    # --- resize ---
    p = subparsers.add_parser("resize", help="Resize the image to exact dimensions")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--size", type=parse_size, required=True, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_resize)

    # --- thumbnail ---
    p = subparsers.add_parser("thumbnail", help="Create a thumbnail (preserves aspect ratio)")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--size", type=parse_size, required=True, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_thumbnail)

    # --- crop ---
    p = subparsers.add_parser("crop", help="Crop a region of the image")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--box", type=parse_box, required=True, metavar="LEFT,TOP,RIGHT,BOTTOM")
    p.set_defaults(func=cmd_crop)

    # --- strip-metadata ---
    p = subparsers.add_parser("strip-metadata", help="Remove metadata from the image")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.set_defaults(func=cmd_strip_metadata)

    # --- batch ---
    p = subparsers.add_parser("batch", help="Batch-process every image in a folder")
    p.add_argument("input_folder", type=Path)
    p.add_argument("output_folder", type=Path)
    p.add_argument(
        "--format",
        default="WEBP",
        type=str.upper,
        choices=["JPEG", "PNG", "WEBP", "AVIF"],
    )
    p.add_argument("--quality", type=int, default=80)
    p.add_argument("--remove-metadata", action="store_true")
    p.add_argument("--resize", type=parse_size, default=None, metavar="WIDTHxHEIGHT")
    p.set_defaults(func=cmd_batch)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
