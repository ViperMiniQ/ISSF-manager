import tkinter as tk
from tkinter import ttk
from datetime import datetime
from datetime import timedelta

import ApplicationProperties
import Changes
import Colors
import CompetitionsInput
import CompetitionsPreview
import Fonts
import HoverInfo
import KeepAspectRatio
import ScrollableFrame
import Tools
import sqlTypes
from CompetitionsDownloader import PreviewToplevel
from CompetitionsPreviewTree import CompetitionsTree
from Logger import benchmark
from dbcommands_rewrite import DBGetter
from typing import List
from CustomWidgets import DateEntry2


class Competitions(tk.Frame):
    @benchmark
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font = Fonts.fonts2["Competitions"]["input"]["font"]
        self.date_entry_style = ttk.Style()
        self.date_entry_style.configure("Competitions.DateEntry", font=self.font)
        self.row_competitions = 0
        self.competitions = []
        self.labels = []

        self.show_tree = 0
        self.x = 800
        self.y = 450

        self.columnconfigure(0, weight=1, uniform="columns")
        self.columnconfigure(1, weight=1, uniform="columns")
        self.columnconfigure(2, weight=1, uniform="columns")

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=10, uniform="rows")

        Changes.subscribe_to_competitions(self)
        KeepAspectRatio.subscribe(self)

        self.treeview_columns = {
            "Naziv": 1,
            "Program": 1,
            "Kategorija": 1,
            "Mjesto": 1,
            "Adresa": 1,
            "Datum": 1,
            "id": 0
        }
        self.treeview_column_widths = {
            "Naziv": 300,
            "Program": 100,
            "Kategorija": 100,
            "Mjesto": 100,
            "Adresa": 150,
            "Datum": 75,
            "id": 1
        }
        self.treeview_column_types = {
            "Naziv": "str",
            "Program": "str",
            "Kategorija": "str",
            "Mjesto": "str",
            "Adresa": "str",
            "Datum": "date",
            "id": "int"
        }

        self.frame_competitions = ScrollableFrame.Vertical(self)
        self.frame_competitions_tree = CompetitionsTree(
            self, self, self.treeview_columns, self.treeview_column_widths,
            self.treeview_column_types, "Competitions",
            Fonts.fonts2["Competitions"]["treeview"]["font"]
        )
        self.frame_competitions_tree.pack_propagate(False)
        self.frame_controls = tk.Frame(self, bg="gray", relief="raised", bd=5)

        self.frame_competitions.scrollable_frame.columnconfigure(0, weight=1, uniform="scr_columns")
        self.frame_competitions.scrollable_frame.columnconfigure(1, weight=10, uniform="scr_columns")
        self.frame_competitions.scrollable_frame.columnconfigure(2, weight=1, uniform="scr_columns")

        self.frame_controls.rowconfigure(0, weight=1, uniform="rows11")
        self.frame_controls.rowconfigure(1, weight=1, uniform="rows11")

        for x in range(0, 4, 1):
            self.frame_controls.columnconfigure(x, weight=1, uniform="columns")
        self.frame_controls.columnconfigure(4, weight=2, uniform="columns")
        self.frame_controls.columnconfigure(5, weight=1, uniform="columns")
        self.frame_controls.columnconfigure(6, weight=2, uniform="columns")

        for x in range(7, 11, 1):
            self.frame_controls.columnconfigure(x, weight=1, uniform="columns")

        current_date = ApplicationProperties.CURRENT_DATE
        current_date_plus_30_days = current_date + timedelta(days=30)

        self.btn_show_as_treeview = tk.Button(
            self.frame_controls,
            text=u"\u2261",
            font=self.font,
            fg="black",
            bg="yellow",
            bd=2,
            command=lambda: self.switch_view()
        )

        self.btn_add_competition = tk.Button(
            self.frame_controls,
            text="+",
            bg="green",
            command=lambda: self.add_new_competition(),
            bd=2,
            font=self.font
        )

        self.btn_color_picker = tk.Button(
            self.frame_controls,
            text=u"\u2699",
            bg="white",
            fg="black",
            font=self.font,
            command=lambda: self.pick_program_colors()
        )
        btn_color_picker_help_text = "Uredi boje prikaza natjecanja prema programu"
        self.btn_treeview_select_columns_help = HoverInfo.create_tooltip(
            widget=self.btn_color_picker,
            text=btn_color_picker_help_text,
            font_size=12,
            anchor="e",
            orientation="right"
        )

        self.btn_hss_competitions = tk.Button(
            self.frame_controls,
            text="HSS",
            bg="green",
            bd=2,
            command=lambda: self.toplevel_hss_natjecanja(),
            font=self.font
        )
        btn_hss_competitions_help_text = "Prikaži/preuzmi HSS natjecanja"
        self.btn_treeview_select_columns_help = HoverInfo.create_tooltip(
            widget=self.btn_hss_competitions,
            text=btn_hss_competitions_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.lbl_calendar_from = tk.Label(
            self.frame_controls,
            font=self.font,
            text="Od:",
            fg="white",
            bg="gray"
        )

        self.calendar_from = DateEntry2(
            self.frame_controls,
            font=self.font,
            selectmode="day",
            state="readonly",
            locale="hr_HR",
            cursor="hand1",
            mindate=datetime.strptime("1900-01-01", "%Y-%m-%d")
        )

        self.lbl_calendar_to = tk.Label(
            self.frame_controls,
            text="Do:",
            font=self.font,
            fg="white",
            bg="gray"
        )

        self.calendar_to = DateEntry2(
            self.frame_controls,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly",
            mindate=datetime.strptime("1900-01-01", "%Y-%m-%d")
        )
        self.calendar_to.set_date(current_date_plus_30_days.strftime("%d. %m. %Y."))

        self.btn_refresh = tk.Button(
            self.frame_controls,
            font=self.font,
            text=u"\u27f3",
            bg="black",
            fg="yellow",
            bd=2,
            command=lambda: self.load_competitions()
        )

        self.frame_competitions_tree.set_colors(
            even_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["bg"],
            odd_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["bg"],
            even_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["fg"],
            odd_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["fg"],
        )

        self.frame_controls.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.frame_competitions.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.frame_competitions_tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.btn_show_as_treeview.grid(row=0, rowspan=2, column=0, sticky="nsew")
        self.btn_add_competition.grid(row=0, rowspan=2, column=1, sticky="nsew")
        self.btn_color_picker.grid(row=0, rowspan=2, column=2, sticky="nsew")

        self.btn_hss_competitions.grid(row=0, rowspan=2, column=10, sticky="nsew")
        self.lbl_calendar_from.grid(row=0, column=4)
        self.calendar_from.grid(row=1, column=4)
        self.lbl_calendar_to.grid(row=0, column=6)
        self.calendar_to.grid(row=1, column=6)
        self.btn_refresh.grid(row=0, rowspan=2, column=5, sticky="nsew")

        self.frame_competitions.lift()
        self.load_competitions()

    def pick_program_colors(self):
        CompetitionsPreview.CompetitionsProgramColorPickerToplevel(self).wait_window()

    def toplevel_hss_natjecanja(self):
        window = PreviewToplevel(self)
        window.focus()
        window.wait_window()

    def update_competitions(self):
        self.load_competitions()
    
    def ShowResults(self, competition_id):
        self.controller.ShowResults(competition_id)

    @benchmark
    def switch_view(self):
        if not self.show_tree:
            self.frame_competitions_tree.lift()
        else:
            self.frame_competitions.lift()
            for c in self.competitions:
                c.check_existence_of_all_files()
        self.show_tree = not self.show_tree

    def clear_competitions(self):
        for child in self.frame_competitions.scrollable_frame.winfo_children():
            child.destroy()
        self.competitions = []
        self.frame_competitions_tree.ClearTree()

    def load_competitions(self):
        print(Fonts.fonts2)

        self.btn_refresh.configure(state="disabled")
        self.configure(cursor="watch")
        self.clear_competitions()

        date_from = self.calendar_from.get_date()
        date_to = self.calendar_to.get_date()

        competitions: List[sqlTypes.CompetitionInfo] = DBGetter.get_competitions_in_time(
            date_from=date_from,
            date_to=date_to
        )

        for competition in competitions:
            self.display_competition(competition)

        self.btn_refresh.configure(state="normal")
        self.frame_competitions_tree.keep_aspect_ratio()
        self.frame_competitions_tree.adjust_all_columns_by_text_length()
        self.configure(cursor="")

    def display_competition(self, values: sqlTypes.CompetitionInfo):
        tree_values = values

        competition = CompetitionsPreview.CompetitionPreview(
            self.frame_competitions.scrollable_frame,
            self,
            values=values
        )

        tree_values["Datum"] = Tools.SQL_date_format_to_croatian(tree_values["Datum"])
        categories_text = ""
        categories = Tools.TranslateCategoriesToList(tree_values["Kategorija"])
        
        for txt in categories:
            categories_text += txt + " | "
            
        categories_text = categories_text[:-2]
        tree_values["Kategorija"] = categories_text
        self.competitions.append(competition)
        self.competitions[-1].grid(row=self.row_competitions, column=1, sticky="nsew")
        self.row_competitions += 1
        self._place_empty_label()
        self.row_competitions += 1
        self.frame_competitions_tree.AddResultToTree(tree_values)

    def _place_empty_label(self):
        self.labels.append(
            tk.Label(
                self.frame_competitions.scrollable_frame, 
                text="", 
                font=self.font
            )
        )
        self.labels[-1].grid(row=self.row_competitions, column=1, sticky="nsew")

    def add_new_competition(self):
        info = CompetitionsInput.CompetitionsInput(self, save=True)
        info.focus()
        info.wait_window()
        if info.values["id"]:
            self.display_competition(info.values)
            Changes.set_competitions()

    def refresh_comboboxes_on_resize(self):
        self.calendar_from.set_date(self.calendar_from.get_date())
        self.calendar_to.set_date(self.calendar_to.get_date())

    def keep_aspect_ratio(self):
        self.calendar_to.configure(font=self.font)
        self.calendar_from.configure(font=self.font)
        self.refresh_comboboxes_on_resize()
