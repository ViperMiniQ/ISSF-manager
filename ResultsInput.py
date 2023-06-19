import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter.constants import END

import Tools
from ResultsNote import Note
import HoverInfo
import KeepAspectRatio
import Fonts
import Colors
from CustomWidgets import CustomBox, DateEntry2


class ResultsInput(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.p = tk.StringVar()
        self.inner = tk.StringVar()
        self.club = tk.StringVar()
        self.competition = tk.StringVar()
        self.target = tk.StringVar()
        self.program = tk.StringVar()
        self.practice = tk.StringVar()
        self.note_text = ""
        self.note_text2 = tk.StringVar()
        self.tips = []

        self.comboboxes = []

        self.selected_shooter = tk.StringVar()
        self.selected_discipline = tk.StringVar()
        self.tree_row_ids = []
        self.cbx_program_values = []
        self.cbx_discipline_values = []
        self.cbx_target_values = []
        self.labels = []
        self.shooter_list = []

        self.text_height = 0

        # grid
        self.rowconfigure(0, weight=5, uniform="rows")
        self.rowconfigure(1, weight=5, uniform="rows")
        self.rowconfigure(2, weight=5, uniform="rows")
        self.rowconfigure(3, weight=2, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")
        self.rowconfigure(5, weight=2, uniform="rows")
        self.rowconfigure(6, weight=1, uniform="rows")
        self.columnconfigure(0, weight=1)

        self.frame_cbxs = tk.Frame(self)
        self.frame_cbxs.grid(row=1, column=0, sticky="nsew")

        self.frame_cbxs_lbls = tk.Frame(self)
        self.frame_cbxs_lbls.grid(row=0, column=0, sticky="nsew")

        self.frame_ents = tk.Frame(self)
        self.frame_ents.grid(row=3, rowspan=3, column=0, sticky="nsew")

        self.frame_ents_lbls = tk.Frame(self)
        self.frame_ents_lbls.grid(row=2, column=0, sticky="nsew")

        self.cbx_ent_font = Fonts.fonts2["Dnevnik"]["unos"]["combobox_entry"]["font"]
        self.cbx_lbx_font = Fonts.fonts2["Dnevnik"]["unos"]["combobox_listbox"]["font"]
        self.lbl_font = Fonts.fonts2["Dnevnik"]["unos"]["labels"]["font"]

        self.date_entry_style = ttk.Style()
        self.date_entry_style.configure("ResultsInput.DateEntry", font=self.cbx_ent_font)

        KeepAspectRatio.subscribe(self)
        Colors.subscribe(self)

        self.r_score = [0, 0, 0, 0, 0, 0]
        self.max_p = 109

        self.validate = (self.register(self.ValiDateEntry2))
        self.validate_note = (self.register(self.CheckNote))
        self.validate_integer = (self.register(Tools.allow_only_integer))

        self.shooters = []

        self.lbl_shooter = tk.Label(
            self.frame_cbxs_lbls,
            text="Strijelac", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_shooter)

        # https://stackoverflow.com/questions/59763822/show-combobox-drop-down-while-editing-text-using-tkinter
        self.cbx_shooter = CustomBox(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            state="readonly"
        )
        self.comboboxes.append(self.cbx_shooter)
        cbx_shooter_help_text = "Aktivni strijelci za unos u dnevnik \n" \
                                "Strijelci se (de)aktiviraju u Pomoć -> Postavke -> Dnevnik > Strijelci \n" \
                                "\n" \
                                "Novi strijelci se dodaju u Rad kluba -> Strijelci"
        self.cbx_shooter_help = HoverInfo.create_tooltip(
            widget=self.cbx_shooter,
            text=cbx_shooter_help_text,
            font_size=12,
            anchor="s",
            orientation="right"
        )

        self.lbl_calendar = tk.Label(
            self.frame_cbxs_lbls,
            text="Datum", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_calendar)

        self.calendar = DateEntry2(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            style="ResultsInput.DateEntry",
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )

        self.lbl_discipline = tk.Label(
            self.frame_cbxs_lbls,
            text="Disciplina", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_discipline)

        self.cbx_discipline = CustomBox(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            state="readonly"
        )
        self.comboboxes.append(self.cbx_discipline)
        self.cbx_discipline.bind("<<ComboboxSelected>>", self.Cbxdiscipline)
        cbx_discipline_help_text = "Aktivne discipline za unos u dnevnik \n" \
                                   "Discipline se (de)aktiviraju u Pomoć -> Postavke -> Dnevnik > Discipline \n" \
                                   "(brisanje dodanih i dodavanje novih vrši se na istom mjestu)"
        self.cbx_discipline_help = HoverInfo.create_tooltip(
            widget=self.cbx_discipline,
            text=cbx_discipline_help_text,
            font_size=12,
            anchor="s",
            orientation="right"
        )

        self.lbl_program = tk.Label(
            self.frame_cbxs_lbls,
            text="Program", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_program)

        self.cbx_program = CustomBox(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            state="readonly"
        )
        self.comboboxes.append(self.cbx_program)
        cbx_program_help_text = "Aktivni programi za unos u dnevnik \n" \
                                "Programi se (de)aktiviraju u Pomoć -> Postavke -> Dnevnik > Programi \n" \
                                "(brisanje dodanih i dodavanje novih vrši se na istom mjestu)"
        self.cbx_program_help = HoverInfo.create_tooltip(
            widget=self.cbx_program,
            text=cbx_program_help_text,
            font_size=12,
            anchor="s",
            orientation="left"
        )

        self.lbl_target = tk.Label(
            self.frame_cbxs_lbls,
            text="Meta", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_target)

        self.cbx_target = CustomBox(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            state="readonly"
        )
        self.comboboxes.append(self.cbx_target)
        cbx_target_help_text = "Aktivne mete za unos u dnevnik \n" \
                               "Mete se (de)aktiviraju u Pomoć -> Postavke -> Dnevnik > Mete \n" \
                               "(brisanje dodanih i dodavanje novih vrši se na istom mjestu)"
        self.cbx_target_help = HoverInfo.create_tooltip(
            widget=self.cbx_target,
            text=cbx_target_help_text,
            font_size=12,
            anchor="s",
            orientation="left"
        )

        self.lbl_competition = tk.Label(
            self.frame_cbxs_lbls,
            text="Natjecanje", 
            fg="white", 
            font=self.lbl_font
        )
        self.labels.append(self.lbl_competition)

        self.cbx_competition = CustomBox(
            self.frame_cbxs,
            font=self.cbx_ent_font,
            state="readonly"
        )
        self.comboboxes.append(self.cbx_competition)
        cbx_competition_help_text = "Aktivna natjecanja za unos u dnevnik \n" \
                                    "Natjecanja se (de)aktiviraju u Pomoć -> Postavke -> Dnevnik > Natjecanja \n" \
                                    "\n" \
                                    "Brisanje dodanih i dodavanje novih vrši se u Rad kluba -> Natjecanja"
        self.cbx_competition_help = HoverInfo.create_tooltip(
            widget=self.cbx_competition,
            text=cbx_competition_help_text,
            font_size=12,
            anchor="s",
            orientation="left"
        )

        self.r_x = []
        for x in range(10, 70, 10):
            r = tk.Label(
                self.frame_ents_lbls,
                text=x,
                fg="white",
                bg="blue",
                font=self.lbl_font
            )
            self.r_x.append(r)

        self.lbl_p = tk.Label(
            self.frame_ents_lbls,
            text="P",
            fg="white",
            bg="blue",
            font=self.lbl_font
        )
        self.labels.append(self.lbl_p)

        self.lbl_inner = tk.Label(
            self.frame_ents_lbls,
            text="*",
            fg="white",
            bg="blue",
            font=self.lbl_font
        )
        self.labels.append(self.lbl_inner)

        self.ent_p = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            validate="all",
            textvariable=self.p,
            bd=3,
            validatecommand=(self.validate_integer, "%P")
        )

        self.ent_r1 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r1")
        )

        self.ent_r2 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r2")
        )

        self.ent_r3 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            state="normal",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r3")
        )

        self.ent_r4 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            state="normal",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r4")
        )

        self.ent_r5 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            state="normal",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r5")
        )

        self.ent_r6 = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            state="normal",
            validate="all",
            bd=3,
            validatecommand=(self.validate, "%P", "%S", "%W", "%s", "ent_r6")
        )

        self.ent_inner = tk.Entry(
            self.frame_ents,
            font=self.cbx_ent_font,
            justify="right",
            textvariable=self.inner,
            validate="all",
            bd=3,
            validatecommand=(self.validate_integer, "%P")
        )

        self.btn_note = tk.Button(
            self.frame_ents,
            text=u"\u2139",
            fg="black",
            bg="gray",
            font=self.cbx_ent_font,
            bd=5,
            command=lambda: self.AddNote()
        )
        self.btn_note.bind("<Return>", lambda event=None: self.btn_note.invoke())

        self.btn_add = tk.Button(
            self.frame_ents,
            fg="black",
            bg="lime",
            text="Dodaj",
            font=self.cbx_ent_font,
            command=lambda: self.Add(),
            bd=5
        )
        self.btn_add.bind("<Return>", lambda event=None: self.btn_add.invoke())

        self.btn_clear = tk.Button(
            self.frame_ents,
            fg="black",
            bg="red2",
            text="Odbaci",
            font=self.cbx_ent_font,
            bd=5,
            command=lambda: self.Clear()
        )
        self.btn_clear.bind("<Return>", lambda event=None: self.btn_clear.invoke())

        self.lbl_score = tk.Label(
            self.frame_ents,
            bg="black",
            fg="white",
            font=self.cbx_ent_font,
        )

        self.frame_note = tk.Frame(self)
        self.frame_note.grid_propagate(False)

        self.frame_note.columnconfigure(0, weight=1, uniform="rows")
        self.frame_note.columnconfigure(1, weight=3, uniform="rows")
        self.frame_note.columnconfigure(2, weight=1, uniform="rows")
        self.frame_note.columnconfigure(3, weight=15, uniform="rows")
        self.frame_note.columnconfigure(4, weight=1, uniform="rows")

        self.lbl_note = tk.Label(
            self.frame_note,
            text="Brza napomena:",
            font=self.cbx_ent_font
        )
        self.labels.append(self.lbl_note)

        self.ent_note = tk.Entry(
            self.frame_note,
            font=self.cbx_ent_font,
            validate="all",
            validatecommand=(self.validate_note, "%P"),
            textvariable=self.note_text2
        )

        self.lbl_note.grid(row=0, column=1, sticky="ew")
        self.ent_note.grid(row=0, column=3, sticky="ew")

        self.grid_cbx_widgets()
        self.grid_cbx_lbl_widgets()
        self.grid_ent_widgets()
        self.grid_ent_lbl_widgets()

        # set colors
        self.load_colors()

        self.bind("<Configure>", self.check_space_for_note)

    def check_space_for_note(self, event=None):
        self.text_height = (self.cbx_ent_font.metrics("linespace") + self.lbl_font.metrics("linespace")) * 3.5
        if self.winfo_height() > self.text_height:
            self.frame_ents.grid_forget()
            self.rowconfigure(0, weight=2, uniform="rows")
            self.rowconfigure(1, weight=2, uniform="rows")
            self.rowconfigure(2, weight=2, uniform="rows")
            self.rowconfigure(3, weight=2, uniform="rows")
            self.rowconfigure(4, weight=1, uniform="rows")
            self.rowconfigure(5, weight=2, uniform="rows")
            self.rowconfigure(6, weight=1, uniform="rows")
            self.frame_ents.grid(row=3, column=0, sticky="nsew")
            self.frame_note.grid(row=5, column=0, sticky="nsew")
            return
        self.rowconfigure(0, weight=5, uniform="rows")
        self.rowconfigure(1, weight=5, uniform="rows")
        self.rowconfigure(2, weight=5, uniform="rows")
        self.rowconfigure(3, weight=2, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")
        self.rowconfigure(5, weight=2, uniform="rows")
        self.rowconfigure(6, weight=1, uniform="rows")
        self.frame_note.grid_forget()
        self.frame_ents.grid_forget()
        self.frame_ents.grid(row=3, rowspan=3, column=0, sticky="nsew")

    def load_colors(self):
        self.change_bg_color(color=Colors.colors["Results"]["input"]["bg"])
        self.change_text_color(color=Colors.colors["Results"]["input"]["fg"])

    def grid_ent_lbl_widgets(self):
        self.frame_ents_lbls.rowconfigure(0, weight=1)

        self.frame_ents_lbls.columnconfigure(0, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(1, weight=3, uniform="frame_ents_cols")  # p
        self.frame_ents_lbls.columnconfigure(2, weight=2, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(3, weight=3, uniform="frame_ents_cols")  # r1
        self.frame_ents_lbls.columnconfigure(4, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(5, weight=3, uniform="frame_ents_cols")  # r2
        self.frame_ents_lbls.columnconfigure(6, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(7, weight=3, uniform="frame_ents_cols")  # r3
        self.frame_ents_lbls.columnconfigure(8, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(9, weight=3, uniform="frame_ents_cols")  # r4
        self.frame_ents_lbls.columnconfigure(10, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(11, weight=3, uniform="frame_ents_cols")  # r5
        self.frame_ents_lbls.columnconfigure(12, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(13, weight=3, uniform="frame_ents_cols")  # r6
        self.frame_ents_lbls.columnconfigure(14, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(15, weight=3, uniform="frame_ents_cols")  # score
        self.frame_ents_lbls.columnconfigure(16, weight=2, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(17, weight=3, uniform="frame_ents_cols")  # inner
        self.frame_ents_lbls.columnconfigure(18, weight=2, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(19, weight=2, uniform="frame_ents_cols")  # i
        self.frame_ents_lbls.columnconfigure(20, weight=2, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(21, weight=4, uniform="frame_ents_cols")  # add
        self.frame_ents_lbls.columnconfigure(22, weight=1, uniform="frame_ents_cols")
        self.frame_ents_lbls.columnconfigure(23, weight=4, uniform="frame_ents_cols")  # clear
        self.frame_ents_lbls.columnconfigure(24, weight=1, uniform="frame_ents_cols")

        self.lbl_p.grid(row=0, column=1)
        self.r_x[0].grid(row=0, column=3)
        self.r_x[1].grid(row=0, column=5)
        self.r_x[2].grid(row=0, column=7)
        self.r_x[3].grid(row=0, column=9)
        self.r_x[4].grid(row=0, column=11)
        self.r_x[5].grid(row=0, column=13)
        self.lbl_inner.grid(row=0, column=17)

    def grid_ent_widgets(self):
        self.frame_ents.rowconfigure(0, weight=1)

        self.frame_ents.columnconfigure(0, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(1, weight=3, uniform="frame_ents_cols")  # p
        self.frame_ents.columnconfigure(2, weight=2, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(3, weight=3, uniform="frame_ents_cols")  # r1
        self.frame_ents.columnconfigure(4, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(5, weight=3, uniform="frame_ents_cols")  # r2
        self.frame_ents.columnconfigure(6, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(7, weight=3, uniform="frame_ents_cols")  # r3
        self.frame_ents.columnconfigure(8, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(9, weight=3, uniform="frame_ents_cols")  # r4
        self.frame_ents.columnconfigure(10, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(11, weight=3, uniform="frame_ents_cols")  # r5
        self.frame_ents.columnconfigure(12, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(13, weight=3, uniform="frame_ents_cols")  # r6
        self.frame_ents.columnconfigure(14, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(15, weight=3, uniform="frame_ents_cols")  # score
        self.frame_ents.columnconfigure(16, weight=2, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(17, weight=3, uniform="frame_ents_cols")  # inner
        self.frame_ents.columnconfigure(18, weight=2, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(19, weight=2, uniform="frame_ents_cols")  # i
        self.frame_ents.columnconfigure(20, weight=2, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(21, weight=4, uniform="frame_ents_cols")  # add
        self.frame_ents.columnconfigure(22, weight=1, uniform="frame_ents_cols")
        self.frame_ents.columnconfigure(23, weight=4, uniform="frame_ents_cols")  # clear
        self.frame_ents.columnconfigure(24, weight=1, uniform="frame_ents_cols")

        self.ent_p.grid(row=0, column=1, sticky="ew")
        self.ent_r1.grid(row=0, column=3, sticky="ew")
        self.ent_r2.grid(row=0, column=5, sticky="ew")
        self.ent_r3.grid(row=0, column=7, sticky="ew")
        self.ent_r4.grid(row=0, column=9, sticky="ew")
        self.ent_r5.grid(row=0, column=11, sticky="ew")
        self.ent_r6.grid(row=0, column=13, sticky="ew")
        self.lbl_score.grid(row=0, column=15, sticky="ew")
        self.ent_inner.grid(row=0, column=17, sticky="ew")
        self.btn_note.grid(row=0, column=19, sticky="ew")
        self.btn_add.grid(row=0, column=21, sticky="ew")
        self.btn_clear.grid(row=0, column=23, sticky="ew")

    def grid_cbx_lbl_widgets(self):
        self.frame_cbxs_lbls.columnconfigure(0, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(1, weight=21, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(2, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(3, weight=15, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(4, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(5, weight=11, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(6, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(7, weight=9, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(8, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(9, weight=10, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(10, weight=1, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(11, weight=33, uniform="cbx_lbls_cols")
        self.frame_cbxs_lbls.columnconfigure(12, weight=1, uniform="cbx_lbls_cols")

        self.frame_cbxs_lbls.rowconfigure(0, weight=1, uniform="cbx_lbls_rows")

        self.lbl_shooter.grid(row=0, column=1, sticky="w")
        self.lbl_calendar.grid(row=0, column=3, sticky="w")
        self.lbl_discipline.grid(row=0, column=5, sticky="w")
        self.lbl_program.grid(row=0, column=7, sticky="w")
        self.lbl_target.grid(row=0, column=9, sticky="w")
        self.lbl_competition.grid(row=0, column=11, sticky="w")

    def grid_cbx_widgets(self):
        self.frame_cbxs.grid_propagate(False)

        self.frame_cbxs.columnconfigure(0, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(1, weight=21, uniform="collsls")
        self.frame_cbxs.columnconfigure(2, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(3, weight=15, uniform="collsls")
        self.frame_cbxs.columnconfigure(4, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(5, weight=11, uniform="collsls")
        self.frame_cbxs.columnconfigure(6, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(7, weight=9, uniform="collsls")
        self.frame_cbxs.columnconfigure(8, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(9, weight=10, uniform="collsls")
        self.frame_cbxs.columnconfigure(10, weight=1, uniform="collsls")
        self.frame_cbxs.columnconfigure(11, weight=33, uniform="collsls")
        self.frame_cbxs.columnconfigure(12, weight=1, uniform="collsls")

        self.frame_cbxs.rowconfigure(0, weight=1, uniform="rowsws")

        self.cbx_shooter.grid(row=0, column=1, sticky="ew")
        self.calendar.grid(row=0, column=3, sticky="ew")
        self.cbx_discipline.grid(row=0, column=5, sticky="ew")
        self.cbx_program.grid(row=0, column=7, sticky="ew")
        self.cbx_target.grid(row=0, column=9, sticky="ew")
        self.cbx_competition.grid(row=0, column=11, sticky="ew")

    def Add(self):
        self.controller.AddButtonPressed()
        self.CheckNote()

    def Clear(self):
        self.controller.ClearButtonPressed()
        self.CheckNote()

    def UpdateShootersList(self, shooters):
        self.shooter_list = shooters
        self.cbx_shooter.configure(values=shooters)

    def UpdateDisciplinesList(self, disciplines):
        self.cbx_discipline.configure(values=disciplines)

    def UpdateProgramsList(self, programs):
        self.cbx_program.configure(values=programs)

    def UpdateTargetsList(self, targets):
        self.cbx_target.configure(values=targets)

    def UpdateCompetitionsList(self, competitions):
        self.cbx_competition.configure(values=competitions)

    def SetBtnAddTitle(self, title):
        self.btn_add.configure(text=title)

    def SetShooter(self, value):
        self.cbx_shooter.set(value)

    def GetShooter(self):
        return self.cbx_shooter.get()

    def SetDiscipline(self, value):
        self.cbx_discipline.set(value)
        self.Cbxdiscipline()

    def GetDiscipline(self):
        return self.cbx_discipline.get()
        
    def SetProgram(self, value):
        self.cbx_program.set(value)

    def GetProgram(self):
        return self.cbx_program.get()

    def SetDate(self, value: datetime.date):
        self.calendar.set_date(value)

    def GetDate(self):
        return self.calendar.get_date()

    def SetTarget(self, value):
        self.cbx_target.set(value)

    def GetTarget(self):
        return self.cbx_target.get()

    def SetCompetition(self, value):
        self.cbx_competition.set(value)

    def GetCompetition(self):
        return self.cbx_competition.get()

    def SetInner(self, value):
        self.ent_inner.delete(0, tk.END)
        self.ent_inner.insert(0, tk.END)

    def GetInner(self):
        return self.ent_inner.get()

    def SetP(self, value):
        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, str(value))

    def GetP(self):
        return self.ent_p.get()

    def SetR10(self, value):
        self.ent_r1.delete(0, tk.END)
        self.ent_r1.insert(0, str(value))

    def GetR10(self):
        return self.r_score[0]

    def SetR20(self, value):
        self.ent_r2.delete(0, tk.END)
        self.ent_r2.insert(0, str(value))

    def GetR20(self):
        return self.r_score[1]

    def SetR30(self, value):
        self.ent_r3.delete(0, tk.END)
        self.ent_r3.insert(0, str(value))

    def GetR30(self):
        return self.r_score[2]

    def SetR40(self, value):
        self.ent_r4.delete(0, tk.END)
        self.ent_r4.insert(0, str(value))

    def GetR40(self):
        return self.r_score[3]

    def SetR50(self, value):
        self.ent_r5.delete(0, tk.END)
        self.ent_r5.insert(0, str(value))

    def GetR50(self):
        return self.r_score[4]

    def SetR60(self, value):
        self.ent_r6.delete(0, tk.END)
        self.ent_r6.insert(0, str(value))

    def GetR60(self):
        return self.r_score[5]

    def SetNote(self, value):
        if value is None:
            value = ""
        self.note_text = str(value)
        self.note_text2.set(value)
        self.CheckNote()

    def CheckNote(self, value=None):
        if value is not None:
            if value:
                self.btn_note.configure(bg="white", fg="blue")
            else:
                self.btn_note.configure(bg="gray", fg="black")
            return True
        if self.note_text2.get():
            self.btn_note.configure(bg="white", fg="blue")
        else:
            self.btn_note.configure(bg="gray", fg="black")
        return True

    def GetEntryValues(self):
        dictionary = {
            "Strijelac": "",
            "Disciplina": "",
            "Program": "",
            "Meta": "",
            "P": "",
            "R10": "",
            "R20": "",
            "R30": "",
            "R40": "",
            "R50": "",
            "R60": "",
            "Ineri": "",
            "Datum": "",
            "Rezultat": "",
            "Natjecanje": "",
            "Napomena": ""
        }

        dictionary["Strijelac"] = self.cbx_shooter.get()
        dictionary["Disciplina"] = self.cbx_discipline.get()
        dictionary["Program"] = self.cbx_program.get()
        dictionary["Meta"] = self.cbx_target.get()
        dictionary["P"] = self.p.get()

        if self.r_score[0] != 0.0:
            dictionary["R10"] = self.r_score[0]
        if self.r_score[1] != 0.0:
            dictionary["R20"] = self.r_score[1]
        if self.r_score[2] != 0.0:
            dictionary["R30"] = self.r_score[2]
        if self.r_score[3] != 0.0:
            dictionary["R40"] = self.r_score[3]
        if self.r_score[4] != 0.0:
            dictionary["R50"] = self.r_score[4]
        if self.r_score[5] != 0.0:
            dictionary["R60"] = self.r_score[5]

        dictionary["Ineri"] = self.ent_inner.get()
        dictionary["Datum"] = self.calendar.get_date()
        dictionary["Rezultat"] = self.lbl_score["text"]
        dictionary["Natjecanje"] = self.cbx_competition.get()
        dictionary["Napomena"] = self.note_text2.get()

        return dictionary

    def CalculateScore(self, r, P):
        if r == "ent_r1":
            self.r_score[0] = P
        if r == "ent_r2":
            self.r_score[1] = P
        if r == "ent_r3":
            self.r_score[2] = P
        if r == "ent_r4":
            self.r_score[3] = P
        if r == "ent_r5":
            self.r_score[4] = P
        if r == "ent_r6":
            self.r_score[5] = P
        score = 0
        for x in range(0, 6, 1):
            score += self.r_score[x]
        score = round(score, 1)
        self.lbl_score["text"] = score

    def ValiDateEntry2(self, P, S, W, s, var):
        entry_r = self.nametowidget(W)
        if "," in P:
            P = P.replace(",", ".")
        if P == "":
            self.CalculateScore(var, 0)
            return True
        try:
            p = float(P)
            if len(P) > 5:
                return False
            entry_r["bg"] = "white"
            self.CalculateScore(var, p)
            if p > self.max_p:
                entry_r["bg"] = "red"
            if not (round(((p - int(p)) * 10), 1).is_integer()):
                entry_r["bg"] = "red"
            return True
        except:
            return False

    def Cbxdiscipline(self, event=None):
        discipline = self.cbx_discipline.get()
        if "60" in discipline:
            self.ent_r3["state"] = "normal"
            self.ent_r4["state"] = "normal"
            self.ent_r5["state"] = "normal"
            self.ent_r6["state"] = "normal"
        elif "40" in discipline:
            self.ent_r3["state"] = "normal"
            self.ent_r4["state"] = "normal"
            self.ent_r5["state"] = "disabled"
            self.ent_r6["state"] = "disabled"
            self.r_score[4] = 0
            self.r_score[5] = 0
        elif "20" in discipline:
            self.ent_r3["state"] = "disabled"
            self.ent_r4["state"] = "disabled"
            self.ent_r5["state"] = "disabled"
            self.ent_r6["state"] = "disabled"
            self.r_score[2] = 0
            self.r_score[3] = 0
            self.r_score[4] = 0
            self.r_score[5] = 0
        else:
            self.ent_r3["state"] = "normal"
            self.ent_r4["state"] = "normal"
            self.ent_r5["state"] = "normal"
            self.ent_r6["state"] = "normal"
        try:
            if discipline[0] == "#":
                self.max_p = 1000
            else:
                self.max_p = 109
        except:
            self.max_p = 109

    def clear_entries(self):
        self.ent_inner.delete(0, END)
        self.ent_p.delete(0, END)
        self.ent_r1.delete(0, END)
        self.ent_r2.delete(0, END)
        self.ent_r3.delete(0, END)
        self.ent_r4.delete(0, END)
        self.ent_r5.delete(0, END)
        self.ent_r6.delete(0, END)
        self.cbx_shooter.set("")
        self.cbx_discipline.set("")
        self.cbx_competition.set("")
        self.cbx_target.set("")
        self.cbx_discipline.set("")
        self.cbx_program.set("")
        self.note_text = ""
        self.note_text2.set("")

        self.Cbxdiscipline(None)
        self.cbx_shooter.focus()

    def change_bg_color(self, color):
        for x in range(0, 6, 1):
            self.r_x[x].configure(bg=color)
        for lbl in self.labels:
            lbl.configure(bg=color)
        self.frame_cbxs.configure(bg=color)
        self.frame_cbxs_lbls.configure(bg=color)
        self.frame_ents.configure(bg=color)
        self.frame_ents_lbls.configure(bg=color)
        self.frame_note.configure(bg=color)
        self.configure(bg=color)

    def change_text_color(self, color):
        for x in range(0, 6, 1):
            self.r_x[x].configure(fg=color)
        for lbl in self.labels:
            lbl.configure(fg=color)

    def refresh_comboboxes_on_resize(self):
        self.cbx_shooter.set(self.cbx_shooter.get())
        self.cbx_discipline.set(self.cbx_discipline.get())
        self.calendar.set_date(self.calendar.get_date())
        self.cbx_program.set(self.cbx_program.get())
        self.cbx_target.set(self.cbx_target.get())
        self.cbx_competition.set(self.cbx_competition.get())

    def AddNote(self):
        note = Note(self, text=self.note_text2.get())
        note.focus()
        note.wait_window()
        if note.text is not None:
            self.note_text2.set(note.text)
        self.CheckNote()

    def keep_aspect_ratio(self):
        self.calendar.configure(font=self.cbx_ent_font)
        self.refresh_comboboxes_on_resize()

# TODO: Hoverinfo, add direction of tooltip besides anchor
