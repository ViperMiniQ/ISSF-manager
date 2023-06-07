import tkinter as tk
import tkinter.font as tkFont
import ScrollableFrame
import ToplevelNewShooter
from ManageArms import NewWeapon, AddNewAirCylinderToplevel
from CompetitionsInput import CompetitionsInput


class ShowAll(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.frame_main = ScrollableFrame.Vertical(self)
        self.frame_main.scrollable_frame.configure(bg="white")
        self.frame_main.pack(expand=True, fill="both")

        self.frame_main.scrollable_frame.columnconfigure(0, weight=1, uniform="cols")
        self.frame_main.scrollable_frame.columnconfigure(1, weight=10, uniform="cols")
        self.frame_main.scrollable_frame.columnconfigure(2, weight=1, uniform="cols")

        self.btn_add_shooter = tk.Button(
            self.frame_main.scrollable_frame,
            text="Dodaj strijelca",
            font=tkFont.Font(size=14),
            command=lambda: ToplevelNewShooter.AddShooter(self).wait_window()
        )

        self.btn_add_weapon = tk.Button(
            self.frame_main.scrollable_frame,
            text="Dodaj oružje",
            font=tkFont.Font(size=14),
            command=lambda: NewWeapon(self).wait_window()
        )

        self.btn_add_air_cylinder = tk.Button(
            self.frame_main.scrollable_frame,
            text="Dodaj cilindar za zrak",
            font=tkFont.Font(size=14),
            command=lambda: AddNewAirCylinderToplevel(self, cylinder_id = 0).wait_window()
        )

        self.btn_add_competition = tk.Button(
            self.frame_main.scrollable_frame,
            text="Dodaj natjecanje",
            font=tkFont.Font(size=14),
            command=lambda: CompetitionsInput(self, save=True).wait_window()
        )

        self.btn_add_shooter.grid(column=1, row=0, sticky="ew", pady=10)
        self.btn_add_weapon.grid(column=1, row=1, sticky="ew", pady=10)
        self.btn_add_air_cylinder.grid(column=1, row=2, sticky="ew", pady=10)
        self.btn_add_competition.grid(column=1, row=3, sticky="ew", pady=10)
