import tkinter as tk
from tkinter import ttk
import CheckbuttonFrame
from CustomWidgets import DateEntry2

import Fonts
import ScrollableFrame
import Tools
from dbcommands_rewrite import DBGetter


class FilterTreeview(tk.Toplevel):
    def __init__(self, master, shooters_radio=False, window_title="Filtriraj prikaz"):
        tk.Toplevel.__init__(self, master)
        self.user_closed = False
        self.title(window_title)
        self.master = master
        self.grab_set()
        self.font = Fonts.fonts2["ResultsFilter"]["date"]["font"]
        self.style = ttk.Style()
        self.style.configure("Size.TCheckbutton", font=Fonts.fonts2["ResultsFilter"]["date"]["font"])

        self.active_programs = {}
        self.active_disciplines = {}
        self.active_competitions = {}
        self.active_targets = {}
        self.active_shooters = {}
        self.date = {
            "to": "1000-01-01",
            "from": "1000-01-01"
        }

        x = 800
        y = 450
        x_min = 800
        y_min = 450

        self.wm_resizable(True, False)

        self.geometry("{}x{}".format(x, y))
        self.minsize(x_min, y_min)
        self.pack_propagate(False)

        self.frame_filter = ScrollableFrame.Horizontal(self)
        self.frame_filter.grid_propagate(False)
        self.frame_filter.scrollable_frame.grid_rowconfigure(0, weight=1)

        style_1 = ttk.Style()
        style_1.configure("SpringGreen2.TFrame", background="SpringGreen2")
        style_2 = ttk.Style()
        style_2.configure("SpringGreen3.TFrame", background="SpringGreen3")

        db_shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters() + DBGetter.get_retired_shooters()

        self.shooters = {}
        shooters = {}
        for shooter in db_shooters:
            self.shooters[shooter["Ime"] + " " + shooter["Prezime"]] = shooter["id"]
            shooters[shooter["Ime"] + " " + shooter["Prezime"]] = 0

        if shooters_radio:
            self.frame_shooters = CheckbuttonFrame.RadiobuttonFrame(
                master=self.frame_filter.scrollable_frame,
                width=300,
                height=300,
                rad_dict=shooters,
                font_size=18,
                color="#00dddd",
                title="Strijelci"
            )
        else:
            self.frame_shooters = CheckbuttonFrame.CheckboxFrame(
                master=self.frame_filter.scrollable_frame,
                width=300,
                height=300,
                cbx_dict=shooters,
                font_size=18,
                color="#00dddd",
                title="Strijelci:"
            )

        self.programs = DBGetter.get_programs_in_results()
        programs = {}
        for program in self.programs:
            programs[program["Naziv"]] = 0

        self.frame_programs = CheckbuttonFrame.CheckboxFrame(
            master=self.frame_filter.scrollable_frame,
            width=300,
            height=300,
            cbx_dict=programs,
            font_size=18,
            color="#00dddd",
            title="Programi:"
        )

        self.disciplines = DBGetter.get_disciplines_in_results()
        disciplines = {}
        for discipline in self.disciplines:
            disciplines[discipline["Naziv"]] = 0

        self.frame_disciplines = CheckbuttonFrame.CheckboxFrame(
            master=self.frame_filter.scrollable_frame,
            width=300,
            height=300,
            cbx_dict=disciplines,
            font_size=18,
            color="#75c0f9",
            title="Discipline:"
        )

        self.targets = DBGetter.get_targets_in_results()
        targets = {}
        for target in self.targets:
            targets[target["Naziv"]] = 0

        self.frame_targets = CheckbuttonFrame.CheckboxFrame(
            master=self.frame_filter.scrollable_frame,
            width=300,
            height=400,
            cbx_dict=targets,
            font_size=18,
            color="#00dddd",
            title="Mete:"
        )

        self.competitions = DBGetter.get_competitions_in_results()
        competitions = {}
        for competition in self.competitions:
            competition["Naziv"] = "(" + Tools.SQL_date_format_to_croatian(competition["Datum"]) + ") " + competition["Naziv"]
            competitions[competition["Naziv"]] = 0

        self.frame_competitions = CheckbuttonFrame.CheckboxFrame(
            master=self.frame_filter.scrollable_frame,
            width=800,
            height=300,
            cbx_dict=competitions,
            font_size=18,
            color="#75c0f9",
            title="Natjecanja:"
        )

        self.frame_date = tk.Frame(self.frame_filter.scrollable_frame, bg="#75c0f9")

        min_date = Tools.SQL_date_format_to_croatian(DBGetter.get_min_date_in_results())
        max_date = Tools.SQL_date_format_to_croatian(DBGetter.get_max_date_in_results())

        self.lbl_date = tk.Label(
            self.frame_date,
            text="Datum:",
            anchor="nw",
            font="Arial 18 bold",
            bg="#75c0f9",
            fg="black"
        )

        self.lbl_calendar_from = tk.Label(
            self.frame_date,
            text="Od:",
            font=self.font,
            bg="#75c0f9",
            fg="black"
        )

        self.calendar_from = DateEntry2(
            self.frame_date,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )
        self.calendar_from.set_date(min_date)

        self.lbl_calendar_to = tk.Label(
            self.frame_date,
            text="Do:",
            font=self.font,
            bg="#75c0f9",
            fg="black"
        )

        self.calendar_to = DateEntry2(
            self.frame_date,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )
        self.calendar_to.set_date(max_date)

        for x in range(0, 6, 1):
            self.frame_date.rowconfigure(x, weight=1)
        self.frame_date.columnconfigure(0, weight=1)

        self.lbl_date.grid(row=0, column=0, sticky="nsew")
        self.lbl_calendar_from.grid(row=1, column=0, sticky="nsew")
        self.calendar_from.grid(row=2, column=0, sticky="ew")
        self.lbl_calendar_to.grid(row=3, column=0, sticky="nsew")
        self.calendar_to.grid(row=4, column=0, stick="ew")

        self.chk_btns = []
        self.values = []
        self.chk_vars = []

        self.btn_confirm = tk.Button(
            self,
            text=u"\u2714",
            font=self.font,
            command=lambda: self.confirm_and_exit(),
            bg="lime",
            fg="black"
        )

        self.btn_confirm.pack(side="top", fill="x")
        self.frame_filter.pack(side="top", fill="both", expand=True)

        self.frame_shooters.grid(row=0, column=0, sticky="ns")
        self.frame_date.grid(row=0, column=1, sticky="ns")
        self.frame_programs.grid(row=0, column=2, sticky="ns")
        self.frame_disciplines.grid(row=0, column=3, sticky="ns")
        self.frame_targets.grid(row=0, column=4, sticky="ns")
        self.frame_competitions.grid(row=0, column=5, sticky="ns")

        self.protocol("WM_DELETE_WINDOW", self.user_close)

    def user_close(self):
        self.user_closed = True
        self.destroy()

    def get_program_id_from_name(self, program: str):
        for p in self.programs:
            if p["Naziv"] == program:
                return p["id"]

    def get_target_id_from_name(self, target: str):
        for t in self.targets:
            if t["Naziv"] == target:
                return t["id"]
        return -1

    def get_discipline_id_from_name(self, discipline: str):
        for d in self.disciplines:
            if d["Naziv"] == discipline:
                return d["id"]
        return -1

    def get_competition_id_from_name(self, competition: str):
        for c in self.competitions:
            if c["Naziv"] == competition:
                return c["id"]
        return -1

    def save_programs_state(self):
        self.active_programs = {}
        programs = self.frame_programs.get_values()
        for key, value in programs.items():
            if value:
                self.active_programs[key] = self.get_program_id_from_name(key)

    def save_targets_state(self):
        self.active_targets = {}
        targets = self.frame_targets.get_values()
        for key, value in targets.items():
            if value:
                self.active_targets[key] = self.get_target_id_from_name(key)

    def save_disciplines_state(self):
        self.active_disciplines = {}
        disciplines = self.frame_disciplines.get_values()
        for key, value in disciplines.items():
            if value:
                self.active_disciplines[key] = self.get_discipline_id_from_name(key)

    def save_competitions_state(self):
        self.active_competitions = {}
        competitions = self.frame_competitions.get_values()
        for key, value in competitions.items():
            if value:
                self.active_competitions[key] = self.get_competition_id_from_name(key)

    def save_dates(self):
        self.date["from"] = str(self.calendar_from.get_date())
        self.date["to"] = str(self.calendar_to.get_date())

    def save_shooters_state(self):
        self.active_shooters = {}
        shooters = self.frame_shooters.get_values()
        for key, value in shooters.items():
            if value:
                try:
                    self.active_shooters[key] = self.shooters[key]
                except KeyError:
                    continue

    def confirm_and_exit(self):
        """Returns only selected values as dict(id, name), date as dict -> ['from'], ['to'] as str"""
        self.save_shooters_state()
        self.save_dates()
        self.save_competitions_state()
        self.save_programs_state()
        self.save_targets_state()
        self.save_disciplines_state()

        self.destroy()
