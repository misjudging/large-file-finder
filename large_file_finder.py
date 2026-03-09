from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a directory and show the largest files."
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="Directory to scan (defaults to current directory)",
    )
    parser.add_argument(
        "--drive",
        type=str,
        default=None,
        help="Windows drive to scan, e.g. C or D:",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=5,
        help="Number of largest files to show (default: 5)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan files directly inside the target directory",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders",
    )
    return parser.parse_args()


def resolve_target(path: Path | None, drive: str | None) -> Path:
    if path is not None and drive is not None:
        raise SystemExit("Use either a path or --drive, not both.")

    if drive is not None:
        drive_letter = drive.rstrip(":").upper()
        if len(drive_letter) != 1 or not drive_letter.isalpha():
            raise SystemExit("Invalid drive. Use a single letter like C or D.")
        return Path(f"{drive_letter}:\\")

    if path is not None:
        return path.resolve()

    return Path.cwd().resolve()


def is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def collect_files(path: Path, recursive: bool, include_hidden: bool) -> list[tuple[Path, int]]:
    iterator = path.rglob("*") if recursive else path.glob("*")
    files: list[tuple[Path, int]] = []
    for item in iterator:
        if not item.is_file():
            continue
        if not include_hidden and is_hidden(item.relative_to(path)):
            continue
        try:
            size = item.stat().st_size
        except OSError:
            continue
        files.append((item, size))
    return files


def main() -> None:
    args = parse_args()
    target = resolve_target(args.path, args.drive)

    if not target.exists() or not target.is_dir():
        raise SystemExit(f"Invalid directory: {target}")
    if args.top < 1:
        raise SystemExit("--top must be at least 1")

    files = collect_files(
        target,
        recursive=not args.no_recursive,
        include_hidden=args.include_hidden,
    )
    files.sort(key=lambda x: x[1], reverse=True)
    top_files = files[: args.top]

    print(f"Scanning: {target}")
    print()
    print(f"Top {len(top_files)} largest files:")
    print()

    for index, (file_path, size) in enumerate(top_files, start=1):
        try:
            display_path = file_path.relative_to(target)
        except ValueError:
            display_path = file_path
        print(f"{index}. {display_path} - {format_size(size)}")


if __name__ == "__main__":
    main()
