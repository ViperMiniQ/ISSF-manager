import tkinter as tk
import tkinter.font as tkFont
from dbcommands_rewrite import DBGetter
from ManageArms import WeaponsDetails


class ShooterWeapons(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.shooter_id = 0
        self.weapons = []
        self.index = 0

        self.font = tkFont.Font(size=14)

        self.frame_commands = tk.Frame(self)

        self.btn_previous = tk.Button(
            self.frame_commands,
            text="<",
            font=self.font,
            command=lambda: self.load_previous_details()
        )

        self.btn_next = tk.Button(
            self.frame_commands,
            text=">",
            font=self.font,
            command=lambda: self.load_next_details()
        )

        self.lbl_no_of = tk.Label(
            self.frame_commands,
            font=self.font,
            text="0/0"
        )

        self.frame_weapon_details = WeaponsDetails(self)

        self.frame_commands.pack(side="top", fill="x")
        self.frame_weapon_details.pack(side="bottom", expand=True, fill="both")

        self.btn_previous.pack(side="left", expand=True, fill="y")
        self.lbl_no_of.pack(side="left", expand=True, fill="y")
        self.btn_next.pack(side="left", expand=True, fill="y")

    def set_shooter_id_and_refresh(self, shooter_id: int):
        self.shooter_id = shooter_id
        self.refresh()
        self.index = 0
        self.load_next_details()

    def refresh(self):
        self.weapons = DBGetter.get_shooter_weapons(self.shooter_id)

    def load_next_details(self):
        self.index += 1
        if len(self.weapons) == self.index:
            self.index = 0
        self.frame_weapon_details.load(self.weapons[self.index]['id'])
        self._set_label()

    def _set_label(self):
        self.lbl_no_of.configure(text=f"{self.index + 1}/{len(self.weapons)}")

    def load_previous_details(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.weapons) - 1
        self.frame_weapon_details.load(self.weapons[self.index]['id'])
        self._set_label()
