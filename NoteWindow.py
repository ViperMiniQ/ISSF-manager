import tkinter as tk
import tkinter.font as tkFont


class NoteWindow(tk.Toplevel):
    def __init__(self, parent, text=""):
        tk.Toplevel.__init__(self, parent)

        self.controller = parent
        self.text = text

        x = 600
        y = 360

        self.geometry("{}x{}".format(x, y))
        self.font = tkFont.Font(size=14)
        self.font_btn = tkFont.Font(size=16)

        self.pack_propagate(False)
        self.txt_note = tk.Text(
            self,
            width=60,
            height=4,
            wrap=tk.WORD,
            font=self.font
        )

        self.btn_increase_font_size = tk.Button(
            self,
            text="A",
            fg="white",
            bg="blue",
            font=self.font_btn,
            command=lambda: self.IncreaseFontSize()
        )

        self.btn_decrease_font_size = tk.Button(
            self,
            text="a",
            fg="white",
            bg="blue",
            font=self.font_btn,
            command=lambda: self.DecreaseFontSize()
        )

        self.txt_note.pack(side="top", expand=True, fill="both")

        self.btn_decrease_font_size.pack(side="left")
        self.btn_increase_font_size.pack(side="left")

        self.txt_note.insert("1.0", self.text)

        self.bind("<Escape>", self.close)

    def close(self, event):
        self.destroy()

    def DecreaseFontSize(self):
        self.font["size"] = self.font["size"] - 1

    def IncreaseFontSize(self):
        self.font["size"] = self.font["size"] + 1
