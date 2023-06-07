import copy
import tkinter as tk
import tkinter.font as tkFont
import CheckbuttonFrame


class ShowShooters(tk.Toplevel):
    def __init__(self, parent, window_title: str, values):
        tk.Toplevel.__init__(self, parent)
        self.title(window_title)
        self.font = tkFont.Font(size=14)
        self.geometry("{}x{}".format(250, 450))
        self.values = copy.deepcopy(values)

        self.btn_confirm = tk.Button(
            self,
            text=u"\u2714",
            font=self.font,
            command=lambda: self.save_and_exit(),
            bg="lime",
            fg="black"
        )

        self.protocol("WM_DELETE_WINDOW", self.exit_pressed)
        self.frame_shooters = CheckbuttonFrame.CheckboxFrame(
            self,
            100,
            100,
            self.values,
            14,
            "deep sky blue",
            "Strijelci"
        )

        self.btn_confirm.pack(side="top", fill="x")
        self.frame_shooters.pack(side="top", expand=True, fill="both")

    def exit_pressed(self):
        self.values = None
        self.destroy()

    def save_and_exit(self):
        self.values = self.frame_shooters.get_values()
        self.destroy()
