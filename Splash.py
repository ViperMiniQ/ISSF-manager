import tkinter as tk
from PIL import ImageTk, Image


class Splash(tk.Toplevel):
    def __init__(self, parent, icon_path, width, height, at_x, at_y):
        tk.Toplevel.__init__(self, parent, width=width, height=height)
        self.overrideredirect(True)
        self.grab_set()
        self.wm_attributes("-transparentcolor", "#F0F0F0")
        self.geometry("{}x{}+{}+{}".format(width, height, at_x, at_y))
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            image=None,
            highlightthickness=0
        )
        self.icon = Image.open(icon_path).convert('RGBA')
        self.icon = self.icon.resize((width, height), Image.ANTIALIAS)
        self.icon = ImageTk.PhotoImage(self.icon)
        self.canvas.create_image(0,0, image=self.icon, anchor="nw")

        self.canvas.pack(expand=True, fill="both")
