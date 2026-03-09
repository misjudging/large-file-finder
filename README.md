# Large File Finder

Fast, no-nonsense CLI tool to find what is eating your disk space.

## What It Does

- Scans any folder (recursively by default)
- Sorts files by size, largest first
- Shows the top N biggest files
- Prints clean, human-readable sizes (`KB`, `MB`, `GB`, etc.)

## Quick Start

```bash
python large_file_finder.py "C:\path\to\folder" --top 5
```

## Example Output

```text
Scanning: C:\Users\ethan\Downloads

Top 5 largest files:

1. movie.mp4 - 1.4 GB
2. game.zip - 820.0 MB
3. video_edit.mov - 620.0 MB
4. dataset.csv - 410.0 MB
5. backup.rar - 350.0 MB
```

## Arguments

- `path`: folder to scan (required)
- `--top`, `-n`: number of files to show (default: `5`)
- `--no-recursive`: only scan files directly inside the selected folder
- `--include-hidden`: include hidden files and folders

## Why Use It

When your storage gets full, this gives you instant visibility into the biggest files so cleanup is easy and targeted.
