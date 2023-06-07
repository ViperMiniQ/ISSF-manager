import tkinter as tk
import tkinter.font as tkFont
import KeepAspectRatio


class DateNote(tk.Frame):
    def __init__(self, controller, parent, text: str, note_id: int, color: str):
        tk.Frame.__init__(self, parent)
        self.txt = text
        self.controller = controller
        self.id = note_id
        self.font = tkFont.Font(size=10)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Obriši", command=lambda: self.Delete())

        self.text = tk.Label(
            self,
            anchor="w",
            justify="left",
            text=text,
            font=self.font,
            bg=color
        )

        self.text.pack(side="top", expand=True, fill="both")
        self.text.bind("<Button-3>", self.show_menu)

        KeepAspectRatio.subscribe(self)

    def Delete(self):
        self.controller.DeleteNote(self.id)

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def SetFont(self, size: int):
        self.font.configure(size=size)

    def keep_aspect_ratio(self):
        self.text.configure(wraplength=KeepAspectRatio.x - 20)
