import tkinter as tk
import tkinter.font as tkFont


class Note(tk.Toplevel):
    def __init__(self, parent, text: str = ""):
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

        self.btn_confirm = tk.Button(
            self,
            text="Spremi",
            fg="black",
            bg="lime",
            width=10,
            font=self.font_btn,
            command=lambda: self.ConfirmAndExit()
        )

        self.txt_note.pack(side="top", expand=True, fill="both")

        self.btn_decrease_font_size.pack(side="left")
        self.btn_increase_font_size.pack(side="left")
        self.btn_confirm.pack(side="right")

        self.txt_note.insert("1.0", self.text)

        self.protocol("WM_DELETE_WINDOW", self.ExitButton)

    def DecreaseFontSize(self):
        self.font["size"] = self.font["size"] - 1

    def IncreaseFontSize(self):
        self.font["size"] = self.font["size"] + 1

    def ExitButton(self):
        self.text = None
        self.destroy()

    def ConfirmAndExit(self):
        text = self.txt_note.get("1.0", tk.END)
        text = text[:-1]
        self.text = text
        self.destroy()
