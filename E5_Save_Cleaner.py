from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox
import pathlib, shutil, struct, zlib, time, re
from typing import List, Tuple

MAGIC_AZP = b"AZP\x01"
LINE_WASDC = re.compile(br"^WasDC\s*$", re.MULTILINE)
DEFAULT_INFO = b"ConsoleInfo  0 0.4 0 \nConsole_end  6160 \n"

class Cleaner:
    def __init__(self):
        self.clean_block: bytes = DEFAULT_INFO  # remembered clean stamp

    # --------------------------------- zlib helpers ---------------------------------
    def streams(self, blob: bytes):
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

    # --------------------------- capture clean ConsoleInfo ---------------------------
    def catch_block(self, path: pathlib.Path):
        raw = path.read_bytes()
        header_len = struct.unpack_from("<I", raw, 4)[0] if raw.startswith(MAGIC_AZP) else 0
        body = raw[header_len:]
        for _, _, plain in self.streams(body):
            m = re.search(br"ConsoleInfo[\s\S]+?Console_end [^\n]*\n", plain)
            if m:
                self.clean_block = m.group(0)
                return True
        return False

    # -------------------------------- patch cheated ---------------------------------
    def patch(self, path: pathlib.Path):
        raw = path.read_bytes()
        header_len = struct.unpack_from("<I", raw, 4)[0] if raw.startswith(MAGIC_AZP) else 0
        header, body = raw[:header_len], raw[header_len:]

        cursor = 0
        out_chunks: List[bytes] = []
        touched = False

        for s, e, plain in self.streams(body):
            changed = False
            if LINE_WASDC.search(plain):
                plain = LINE_WASDC.sub(b"", plain)
                changed = True
            if b"ConsoleInfo" in plain:
                plain = re.sub(br"ConsoleInfo[\s\S]+?Console_end [^\n]*\n", self.clean_block, plain, count=1)
                changed = True
            if changed:
                touched = True
                comp = zlib.compress(plain)
                comp = comp[: e - s] + b"\x00" * max(0, (e - s) - len(comp)) if len(comp) > e - s else comp + b"\x00" * ((e - s) - len(comp))
                out_chunks.append(body[cursor:s] + comp)
            else:
                out_chunks.append(body[cursor:e])
            cursor = e
        out_chunks.append(body[cursor:])
        if not touched:
            return False
        backup = path.with_suffix(path.suffix + f".bak_{int(time.time())}")
        shutil.copy2(path, backup)
        path.write_bytes(header + b"".join(out_chunks))
        return True

# -------------------------------------- GUI ----------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brigade E5 Cycle‑Safe Save Cleaner")
        self.geometry("540x300")
        self.cleaner = Cleaner()

        instr = (
            "Instructions:\n"
            "1. Turn off **Steam Cloud** in the game properties.\n"
            "2. Pause the game → create a clean save → **Catch Encryption Cycle**.\n"
            "3. Cheat → save again → **Clean Cheated Save**.\n\n"
            "• Game must be paused during the process.\n"
            "• Original files are backed up next to the modified save."
        )
        tk.Label(self, text=instr, justify="left", anchor="w").pack(pady=6, padx=8, fill="x")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Catch Encryption Cycle", width=28, command=self.catch_cycle).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Clean Cheated Save", width=28, command=self.clean_cheated).pack(side=tk.LEFT, padx=8)

        self.status = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status, fg="blue").pack(pady=10)

    def ask_file(self):
        return filedialog.askopenfilename(filetypes=[("Save files", "*.nsv *.dat")])

    def catch_cycle(self):
        f = self.ask_file()
        if not f:
            return
        try:
            if self.cleaner.catch_block(pathlib.Path(f)):
                self.status.set("✔ Captured clean block from " + pathlib.Path(f).name)
            else:
                messagebox.showerror("Error", "Couldn't locate ConsoleInfo in that save.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clean_cheated(self):
        f = self.ask_file()
        if not f:
            return
        try:
            if self.cleaner.patch(pathlib.Path(f)):
                self.status.set("✔ Patched " + pathlib.Path(f).name + " (backup created)")
            else:
                self.status.set("No changes needed for " + pathlib.Path(f).name)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()
