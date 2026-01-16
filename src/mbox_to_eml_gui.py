import os
import argparse
import mailbox
import email
import re
from email.utils import parsedate_to_datetime
from email.header import decode_header, make_header
from typing import Optional, Callable
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Prudential limit for full path length on Windows (approx. MAX_PATH ~260)
MAX_TOTAL_PATH_LEN = 250


def decode_subject(raw_subject: str) -> str:
    """
    Decode the Subject header into Unicode, handling encoded-words like =?utf-8?b?...?=
    """
    if not raw_subject:
        return ""
    try:
        decoded = str(make_header(decode_header(raw_subject)))
        return decoded
    except Exception:
        return raw_subject


def sanitize_filename(name: str) -> str:
    """
    Make a string safe for use as a filename:
    - normalize whitespace
    - replace characters invalid on Windows/POSIX
    """
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip().rstrip(".")
    if not name:
        name = "no_subject"
    return name


def get_message_date(msg) -> str:
    """
    Return message date as 'dd-mm-YYYY'.
    If date is not parseable, return '00-00-0000'.
    """
    date_header = msg.get('Date')
    if not date_header:
        return "00-00-0000"
    try:
        dt = parsedate_to_datetime(date_header)
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return "00-00-0000"


def build_filename(base_name: str, date_str: str, max_filename_len: int,
                   index: Optional[int] = None) -> str:
    """
    Build the final filename applying:
    - sanitized base_name
    - date part _dd-mm-YYYY
    - optional _index for duplicates
    - .eml extension

    If the total length exceeds max_filename_len, truncate base_name.
    """
    suffix = f"_{date_str}"
    if index is not None:
        suffix += f"_{index}"
    suffix += ".eml"
    allowed_base_len = max_filename_len - len(suffix)
    if allowed_base_len <= 0:
        allowed_base_len = 1
    if len(base_name) > allowed_base_len:
        base_name = base_name[:allowed_base_len]
    return base_name + suffix


def compute_max_filename_len(output_dir: str) -> int:
    """
    Compute how many characters are available for the FILE NAME
    taking into account the full path limit.
    """
    sample_path = os.path.join(output_dir, "x")
    base_dir_len = len(sample_path) - 1
    max_filename_len = MAX_TOTAL_PATH_LEN - base_dir_len
    if max_filename_len < 50:
        max_filename_len = 50
    return max_filename_len


def export_mbox_to_eml(mbox_path: str, output_dir: str,
                       status_callback: Optional[Callable[[int, int, Optional[str]], None]] = None):
    """
    Export messages from an MBOX file to individual .eml files.
    status_callback(current: int, total: int, info: Optional[str])
    If status_callback is None, messages are printed to stdout.
    """
    def _log(msg: str):
        if status_callback:
            try:
                status_callback(-1, -1, msg)
            except Exception:
                pass
        else:
            print(msg)

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            _log(f"Folder created: {output_dir}")
        except OSError as e:
            _log(f"[ERROR] Unable to create folder '{output_dir}': {e}")
            return

    try:
        mbox = mailbox.mbox(mbox_path)
    except Exception as e:
        _log(f"[ERROR] Unable to open MBOX '{mbox_path}': {e}")
        return

    try:
        total = len(mbox)
    except Exception:
        total = -1

    max_filename_len = compute_max_filename_len(output_dir)

    for i, msg in enumerate(mbox):
        raw_subject = msg.get('Subject', '')
        decoded_subject = decode_subject(raw_subject)
        subject = sanitize_filename(decoded_subject)
        date_str = get_message_date(msg)
        filename = build_filename(subject, date_str, max_filename_len)
        base_for_duplicates = subject
        index = 1
        final_path = os.path.join(output_dir, filename)
        while os.path.exists(final_path):
            filename = build_filename(base_for_duplicates, date_str,
                                      max_filename_len, index=index)
            final_path = os.path.join(output_dir, filename)
            index += 1
        try:
            with open(final_path, "wb") as f:
                if isinstance(msg, mailbox.mboxMessage):
                    f.write(msg.as_bytes())
                elif isinstance(msg, email.message.Message):
                    f.write(msg.as_bytes())
                else:
                    f.write(bytes(str(msg), "utf-8", errors="replace"))
            # update progress: current, total, info (saved path)
            if status_callback:
                try:
                    status_callback(i + 1, total, final_path)
                except Exception:
                    pass
            else:
                print(f"[{i+1}] Saved: {final_path}")
        except OSError as e:
            _log(f"[ERROR] Unable to save '{final_path}': {e}")
            continue


def create_gui():
    root = tk.Tk()
    root.title("MBOX → EML")
    root.resizable(True, True)

    frm = ttk.Frame(root, padding=5)
    frm.pack(fill=tk.BOTH, expand=True)
    frm.rowconfigure(3, weight=1)
    frm.columnconfigure(1, weight=1)

    # MBOX file
    ttk.Label(frm, text="MBOX file:").grid(row=0, column=0, sticky=tk.W, pady=3, padx=5)
    mbox_var = tk.StringVar()
    mbox_entry = ttk.Entry(frm, textvariable=mbox_var, width=50)
    mbox_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=(5, 5), pady=3)
    def browse_mbox():
        p = filedialog.askopenfilename(title="Select MBOX file",
                                       filetypes=[("MBOX", "*.mbox;*.mbx"), ("All files", "*.*")])
        if p:
            mbox_var.set(p)
    ttk.Button(frm, text="Browse...", command=browse_mbox).grid(row=0, column=3, padx=(5, 5), pady=3)

    # Output dir
    ttk.Label(frm, text="Output folder:").grid(row=1, column=0, sticky=tk.W, pady=3, padx=5)
    out_var = tk.StringVar()
    out_entry = ttk.Entry(frm, textvariable=out_var, width=50)
    out_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=(5, 5), pady=3)
    def browse_out():
        p = filedialog.askdirectory(title="Select output folder")
        if p:
            out_var.set(p)
    ttk.Button(frm, text="Browse...", command=browse_out).grid(row=1, column=3, padx=(5, 5), pady=3)

    # Progress bar
    ttk.Label(frm, text="Progress:").grid(row=2, column=0, sticky=tk.W, pady=3, padx=5)
    progress = ttk.Progressbar(frm, orient=tk.HORIZONTAL, mode='determinate')
    progress.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=(5, 5), pady=3)
    progress_label = ttk.Label(frm, text="0/0")
    progress_label.grid(row=2, column=3, sticky=tk.W, padx=(5, 5), pady=3)

    # Spacer row to push buttons to the bottom
    spacer = ttk.Frame(frm)
    spacer.grid(row=3, column=0, columnspan=4, sticky=tk.NSEW)

    # Buttons frame
    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=4, column=0, columnspan=4, pady=(5, 5), padx=5, sticky=tk.EW)

    start_btn = ttk.Button(btn_frame, text="Start")
    start_btn.pack(side=tk.RIGHT)
    close_btn = ttk.Button(btn_frame, text="Close", command=root.destroy)
    close_btn.pack(side=tk.RIGHT, padx=10)

    q: "queue.Queue[tuple]" = queue.Queue()

    def poll_queue():
        try:
            while True:
                item = q.get_nowait()
                if not isinstance(item, tuple):
                    continue
                tag = item[0]
                if tag == "progress":
                    _, current, total = item
                    if total and total > 0:
                        progress['maximum'] = total
                        progress['value'] = current
                        progress_label.config(text=f"{current}/{total}")
                    else:
                        progress.config(mode='indeterminate')
                        if not progress_label.cget("text").endswith(" (processing)"):
                            progress_label.config(text="Processing")
                        try:
                            progress.start(50)
                        except Exception:
                            pass
                elif tag == "done":
                    _, out_dir = item
                    progress.stop()
                    progress.config(mode='determinate')
                    if progress['value'] == 0:
                        progress_label.config(text="0/0")
                    open_it = messagebox.askyesno("Operation completed",
                                                  f"Extraction completed.\nOpen the output folder?\n\n{out_dir}")
                    if open_it:
                        try:
                            os.startfile(out_dir)
                        except Exception as e:
                            messagebox.showerror("Error", f"Unable to open the folder: {e}")
                elif tag == "error":
                    _, msg = item
                    progress.stop()
                    messagebox.showerror("Error", msg)
        except queue.Empty:
            pass
        if worker_thread and worker_thread.is_alive():
            root.after(100, poll_queue)
        else:
            start_btn.config(state=tk.NORMAL)

    worker_thread = None

    def start_export():
        nonlocal worker_thread
        mbox_path = mbox_var.get().strip()
        out_dir = out_var.get().strip()
        if not mbox_path or not os.path.isfile(mbox_path):
            messagebox.showerror("Error", "Specify a valid MBOX file.")
            return
        if not out_dir:
            messagebox.showerror("Error", "Specify the output folder.")
            return

        start_btn.config(state=tk.DISABLED)
        progress.config(mode='determinate', value=0)
        progress_label.config(text="0/0")

        def status_cb(current: int, total: int, info: Optional[str]):
            if current == -1 and total == -1 and info and info.startswith("[ERROR]"):
                q.put(("error", info))
            else:
                q.put(("progress", current, total))

        def target():
            try:
                export_mbox_to_eml(mbox_path, out_dir, status_callback=status_cb)
                q.put(("done", out_dir))
            except Exception as e:
                q.put(("error", f"[ERROR] {e}"))

        worker_thread = threading.Thread(target=target, daemon=True)
        worker_thread.start()
        root.after(100, poll_queue)

    start_btn.config(command=start_export)

    # Resize window to fit content
    root.update_idletasks()
    min_width = frm.winfo_reqwidth() + 10
    min_height = frm.winfo_reqheight() + 10
    root.geometry(f"{min_width}x{min_height}")
    
    # Set minimum window size
    root.minsize(min_width, min_height)

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description="Extract messages from an MBOX file into individual .eml files "
                    "named using subject and date, handling long names and invalid characters."
    )

    parser.add_argument("mbox_file", nargs="?", help="Path to source .mbox file")
    parser.add_argument("output_dir", nargs="?", help="Folder to save .eml files")
    parser.add_argument("--gui", action="store_true", help="Open the graphical interface")

    args = parser.parse_args()

    if args.gui or (not args.mbox_file and not args.output_dir):
        create_gui()
        return

    if not os.path.isfile(args.mbox_file):
        print("Error: the specified MBOX file does not exist.")
        return

    export_mbox_to_eml(args.mbox_file, args.output_dir)


if __name__ == "__main__":
    # Check if running in Docker (simple heuristic: check for /.dockerenv or env var)
    is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    
    if len(sys.argv) == 1 and not is_docker:
        create_gui()
    else:
        main()
