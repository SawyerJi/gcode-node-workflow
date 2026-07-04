#!/usr/bin/env python3
"""Split a sliced model G-code at a Z boundary and insert cutting G-code."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


Z_MOVE_RE = re.compile(r"(?<![A-Za-z])Z\s*([-+]?\d*\.?\d+)", re.IGNORECASE)
GCODE_COMMAND_RE = re.compile(r"^\s*(G0|G1)\b", re.IGNORECASE)


def strip_comment(line: str) -> str:
    """Remove semicolon comments before parsing motion words."""
    return line.split(";", 1)[0]


def parse_z_move(line: str) -> float | None:
    """Return the Z value from a G0/G1 move, if present."""
    command = strip_comment(line)
    if not GCODE_COMMAND_RE.search(command):
        return None
    match = Z_MOVE_RE.search(command)
    if not match:
        return None
    return float(match.group(1))


def split_model_gcode(lines: list[str], boundary_mm: float) -> tuple[list[str], list[str], int]:
    """Split model G-code after the first movement reaching the boundary."""
    split_after_index: int | None = None

    for index, line in enumerate(lines):
        z = parse_z_move(line)
        if z is not None and z >= boundary_mm:
            split_after_index = index
            break

    if split_after_index is None:
        raise ValueError(
            "Could not find a G0/G1 Z move at or above "
            f"{boundary_mm:g}mm in the model G-code."
        )

    return (
        lines[: split_after_index + 1],
        lines[split_after_index + 1 :],
        split_after_index + 1,
    )


def section(title: str) -> list[str]:
    return [
        "\n",
        f"; ---- {title} ----\n",
    ]


def build_final_gcode(x_lines: list[str], z_lines: list[str], y_lines: list[str]) -> list[str]:
    output: list[str] = []
    output.extend(section("BEGIN X: MODEL PRINT BEFORE/AT 6MM"))
    output.extend(x_lines)
    output.extend(section("END X"))
    output.extend(section("WAIT BEFORE CUTTING"))
    output.append("G4 S10\n")
    output.extend(section("BEGIN Z: IMPORTED CUTTING G-CODE"))
    output.extend(z_lines)
    output.extend(section("END Z"))
    output.extend(section("WAIT BEFORE Y"))
    output.append("G4 S10\n")
    output.extend(section("BEGIN Y: MODEL PRINT AFTER 6MM"))
    output.extend(y_lines)
    output.extend(section("END Y"))
    return output


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split sliced model G-code at a Z boundary and insert cutting G-code."
    )
    parser.add_argument("--model", required=True, type=Path, help="Already-sliced model G-code.")
    parser.add_argument("--cutting", required=True, type=Path, help="Imported cutting G-code.")
    parser.add_argument("--out", required=True, type=Path, help="Merged output G-code.")
    parser.add_argument("--x-out", type=Path, help="Optional output path for extracted X G-code.")
    parser.add_argument("--y-out", type=Path, help="Optional output path for extracted Y G-code.")
    parser.add_argument("--boundary", type=float, default=6.0, help="Split boundary in mm. Default: 6.")
    args = parser.parse_args()

    model_lines = args.model.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    cutting_lines = args.cutting.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

    x_lines, y_lines, split_line = split_model_gcode(model_lines, args.boundary)
    final_lines = build_final_gcode(x_lines, cutting_lines, y_lines)

    write_lines(args.out, final_lines)
    if args.x_out:
        write_lines(args.x_out, x_lines)
    if args.y_out:
        write_lines(args.y_out, y_lines)

    print(f"Boundary: {args.boundary:g}mm")
    print(f"Split after model G-code line: {split_line}")
    print(f"X lines: {len(x_lines)}")
    print(f"Z lines: {len(cutting_lines)}")
    print(f"Y lines: {len(y_lines)}")
    print(f"Merged output: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
