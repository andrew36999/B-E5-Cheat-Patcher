from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pathlib, shutil, struct, time, zlib, re, sys, os

MAGIC_AZP = b"AZP\x01"
TARGET_INFO = b"ConsoleInfo  0 0.4 0 \n"
TARGET_END  = b"Console_end  6160 \n"
LINE_WASDC  = re.compile(br"^WasDC\s*$", re.MULTILINE)

def find_streams(blob: bytes):
    i = 0
    while i < len(blob) - 2:
        if blob[i] == 0x78 and blob[i + 1] in (0x01, 0x5E, 0x9C, 0xDA):
            d = zlib.decompressobj()
            try:
                dec = d.decompress(blob[i:])
                end = i + len(blob[i:]) - len(d.unused_data)
                yield i, end, dec
                i = end
            except zlib.error:
                i += 1
        else:
            i += 1

def patch_stream(data: bytes) -> bytes:
    changed = False

    if LINE_WASDC.search(data):
        data = LINE_WASDC.sub(b"", data)
        changed = True

    m_info = re.search(br"ConsoleInfo[^\n]*\n", data)
    m_end  = re.search(br"Console_end [^\n]*\n", data)
    if m_info and m_end:
        start, end = m_info.start(), m_end.end()
        data = data[:start] + TARGET_INFO + TARGET_END + data[end:]
        changed = True
    return data, changed


def patch_save(path: pathlib.Path):
    raw = path.read_bytes()
    header_len = struct.unpack_from("<I", raw, 4)[0] if raw.startswith(MAGIC_AZP) else 0
    header, body = raw[:header_len], raw[header_len:]

    cursor = 0
    out = []
    touched = False

    for s, e, plain in find_streams(body):
        patched_plain, dirty = patch_stream(plain)
        if not dirty:
            out.append(body[cursor:e])
        else:
            touched = True
            comp = zlib.compress(patched_plain)
            comp += b"\x00" * (e - s - len(comp)) if len(comp) < (e - s) else comp[: e - s]
            out.append(body[cursor:s] + comp)
        cursor = e
    out.append(body[cursor:])

    if not touched:
        return False

    backup = path.with_suffix(path.suffix + f".bak_{int(time.time())}")
    shutil.copy2(path, backup)
    path.write_bytes(header + b"".join(out))
    return True


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E5 Save Cleaner")
        self.geometry("480x240")

        self.folder = tk.StringVar()
        self.listbox = tk.Listbox(self, height=8, width=60)
        self.listbox.pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack()
        tk.Button(btn_frame, text="Choose Save Folder", command=self.choose_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Patch Selected", command=self.patch_selected).pack(side=tk.LEFT, padx=5)

    def choose_folder(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        self.folder.set(directory)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        p = pathlib.Path(self.folder.get())
        for f in p.glob("*.nsv"):
            self.listbox.insert(tk.END, f.name)
        for f in p.glob("*.dat"):
            self.listbox.insert(tk.END, f.name)

    def patch_selected(self):
        if not self.listbox.curselection():
            messagebox.showwarning("No file", "Please select a save file first.")
            return
        filename = self.listbox.get(self.listbox.curselection()[0])
        path = pathlib.Path(self.folder.get()) / filename
        try:
            if patch_save(path):
                messagebox.showinfo("Done", f"Patched {filename} and created backup.")
            else:
                messagebox.showinfo("No change", f"{filename} already clean.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()
