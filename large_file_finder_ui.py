from __future__ import annotations

import ctypes
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from large_file_finder import collect_files, format_size


def list_windows_drives() -> list[str]:
    drives: list[str] = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            drives.append(f"{chr(65 + i)}:\\")
    return drives


class LargeFileFinderUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Large File Finder")
        self.root.geometry("920x600")
        self.root.minsize(820, 520)

        self.top_var = tk.IntVar(value=20)
        self.status_var = tk.StringVar(value="Choose a drive to scan.")
        self.scanning = False

        self.drive_buttons: list[ttk.Button] = []

        self._build_ui()
        self._create_drive_buttons()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Large File Finder",
            font=("Segoe UI", 18, "bold"),
        )
        header.pack(anchor=tk.W)

        subtitle = ttk.Label(
            container,
            text="Pick a drive, scan, and review the biggest files quickly.",
        )
        subtitle.pack(anchor=tk.W, pady=(2, 12))

        controls = ttk.Frame(container)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Top files:").pack(side=tk.LEFT)
        top_spin = ttk.Spinbox(controls, from_=1, to=500, textvariable=self.top_var, width=6)
        top_spin.pack(side=tk.LEFT, padx=(8, 0))

        self.progress = ttk.Progressbar(controls, mode="indeterminate", length=180)
        self.progress.pack(side=tk.RIGHT)

        drives_section = ttk.LabelFrame(container, text="Drives", padding=10)
        drives_section.pack(fill=tk.X, pady=(12, 10))
        self.drives_frame = ttk.Frame(drives_section)
        self.drives_frame.pack(fill=tk.X)

        results_section = ttk.LabelFrame(container, text="Largest Files", padding=10)
        results_section.pack(fill=tk.BOTH, expand=True)

        columns = ("file", "size")
        self.tree = ttk.Treeview(results_section, columns=columns, show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("size", text="Size")
        self.tree.column("file", width=680, anchor=tk.W)
        self.tree.column("size", width=160, anchor=tk.E)

        scrollbar = ttk.Scrollbar(results_section, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        status = ttk.Label(container, textvariable=self.status_var)
        status.pack(fill=tk.X, pady=(8, 0))

    def _create_drive_buttons(self) -> None:
        for widget in self.drives_frame.winfo_children():
            widget.destroy()

        drives = list_windows_drives()
        if not drives:
            self.status_var.set("No drives detected.")
            return

        for drive in drives:
            btn = ttk.Button(
                self.drives_frame,
                text=drive,
                command=lambda d=drive: self.start_scan(d),
                width=8,
            )
            btn.pack(side=tk.LEFT, padx=(0, 8), pady=2)
            self.drive_buttons.append(btn)

    def start_scan(self, drive: str) -> None:
        if self.scanning:
            return

        try:
            top_n = int(self.top_var.get())
        except (tk.TclError, ValueError):
            self.status_var.set("Top files must be a number.")
            return

        if top_n < 1:
            self.status_var.set("Top files must be at least 1.")
            return

        self.scanning = True
        self._set_buttons_state("disabled")
        self.progress.start(10)
        self.status_var.set(f"Scanning {drive} ...")
        self.tree.delete(*self.tree.get_children())

        worker = threading.Thread(target=self._scan_worker, args=(drive, top_n), daemon=True)
        worker.start()

    def _scan_worker(self, drive: str, top_n: int) -> None:
        try:
            target = Path(drive)
            files = collect_files(target, recursive=True, include_hidden=False)
            files.sort(key=lambda x: x[1], reverse=True)
            top_files = files[:top_n]
            self.root.after(0, self._scan_done, drive, top_files, "")
        except Exception as exc:  # pragma: no cover
            self.root.after(0, self._scan_done, drive, [], str(exc))

    def _scan_done(self, drive: str, top_files: list[tuple[Path, int]], error: str) -> None:
        self.progress.stop()
        self._set_buttons_state("normal")
        self.scanning = False

        if error:
            self.status_var.set(f"Scan failed for {drive}: {error}")
            return

        for file_path, size in top_files:
            self.tree.insert("", tk.END, values=(str(file_path), format_size(size)))

        self.status_var.set(f"Done. Found {len(top_files)} largest files on {drive}.")

    def _set_buttons_state(self, state: str) -> None:
        for btn in self.drive_buttons:
            btn.configure(state=state)


def main() -> None:
    root = tk.Tk()
    app = LargeFileFinderUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
