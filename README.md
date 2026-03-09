# Large File Finder

Simple CLI tool that scans a folder and shows the largest files taking up space.

## Usage

```bash
python large_file_finder.py "C:\path\to\folder" --top 5
```

## Options

- `--top` / `-n`: number of files to show (default: 5)
- `--no-recursive`: scan only the selected folder
- `--include-hidden`: include hidden files/folders
