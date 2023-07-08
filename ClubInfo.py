import tkinter as tk
import Fonts
from dbcommands_rewrite import DBGetter, DBUpdate

# should mimic HSS-IS club information page


class ClubInfo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font = Fonts.fonts2["ClubInfo"]["labels"]["font"]

        self.lbl_title = tk.Label(
            self,
            text="Naziv: ",
            font=self.font
        )

        self.ent_title = tk.Entry(
            self,
            font=self.font
        )

        self.lbl_location = tk.Label(
            self,
            text="Mjesto: ",
            font=self.font
        )

        self.ent_location = tk.Entry(
            self,
            font=self.font
        )

        self.btn_save_changes = tk.Button(
            self,
            text="Spremi",
            bg="lime",
            font=self.font,
            command=lambda: self.save_changes()
        )

        for x in range(0, 10, 1):
            self.columnconfigure(x, weight=1, uniform="cols")
        for y in range(0, 10, 1):
            self.rowconfigure(y, weight=1, uniform="rows")

        self.lbl_title.grid(row=1, column=1, sticky="e")
        self.ent_title.grid(row=1, column=2, columnspan=2, sticky="ew")
        self.lbl_location.grid(row=3, column=1, sticky="e")
        self.ent_location.grid(row=3, column=2, columnspan=2, sticky="ew")

        self.btn_save_changes.grid(row=8, column=8, sticky="nsew")

        self.load_information()

    def load_information(self):
        self.ent_location.delete(0, tk.END)
        self.ent_location.insert(0, str(DBGetter.get_club_location()))

        self.ent_title.delete(0, tk.END)
        self.ent_title.insert(0, str(DBGetter.get_club_name()))

    def save_changes(self):
        DBUpdate.set_club_title_and_location(
            title=self.ent_title.get(),
            location=self.ent_location.get()
        )
        self.load_information()
