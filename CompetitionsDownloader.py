import datetime

import Calendar
import Colors
import logging
import Tools
import sqlTypes
from ResultsTree import ResultsTree
import Downloader
import tkinter as tk
from tkinter import messagebox
import Fonts
from CompetitionsInput import CompetitionsInput
from dbcommands_rewrite import DBGetter, DBAdder, DBRemover
import threading
import HoverInfo


class PreviewToplevel(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.title("HSS natjecanja")

        self.geometry("800x600")
        self.grab_set()

        self.preview = Preview(self)

        self.preview.pack(expand=True, fill="both")
        self.after(100, lambda: self.preview.preview_competitions())

        self.bind("<Configure>", self.preview.frame_tree.adjust_all_columns_by_text_length)


class Preview(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.tree_cols = {
            "hss_id": 1,
            "Naziv": 1,
            "Datum": 1,
            "Mjesto": 1,
            "Unešeno": 1
        }

        self.tree_cols_width = {
            "hss_id": 10,
            "Naziv": 200,
            "Datum": 50,
            "Mjesto": 50,
            "Unešeno": 10
        }

        self.tree_cols_types = {
            "hss_id": "int",
            "Naziv": "str",
            "Datum": "date",
            "Mjesto": "str",
            "Unešeno": "str"
        }

        self.font = Fonts.fonts2["Competitions"]["Downloader"]["treeview"]["font"]

        self.selected_symbol = u"\u2714"

        self.frame_tree = ResultsTree(self, self, self.tree_cols, self.tree_cols_width, self.tree_cols_types,
                                      "CompetitionsDownloader", self.font)

        self.frame_tree.set_colors(
            odd_row_bg=Colors.colors["CompetitionsDownloader"]["treeview"]["odd_rows"]["bg"],
            odd_row_fg=Colors.colors["CompetitionsDownloader"]["treeview"]["odd_rows"]["fg"],
            even_row_bg=Colors.colors["CompetitionsDownloader"]["treeview"]["even_rows"]["bg"],
            even_row_fg=Colors.colors["CompetitionsDownloader"]["treeview"]["even_rows"]["fg"]
        )

        self.menu = tk.Menu(
            self.frame_tree,
            font=self.font,
            tearoff=0
        )

        self.frame_buttons = tk.Frame(self)

        self.btn_download_new = tk.Button(
            self.frame_buttons,
            text=u"\u21E9",
            bg="green",
            fg="white",
            font=self.font,
            command=lambda: self.new_thread()
        )
        btn_download_new_help_text = """Preuzimanje novih natjecanja sa službene stranice streljačkog saveza"""
        self.btn_download_new_help = HoverInfo.create_tooltip(
            widget=self.btn_download_new,
            text=btn_download_new_help_text,
            font_size=12,
            anchor="s",
            orientation="right"
        )

        self.btn_delete_all = tk.Button(
            self.frame_buttons,
            text=u"\u2421",
            bg="red",
            fg="white",
            font=self.font,
            command=lambda: self.delete_all()
        )
        btn_delete_all_help_text = """
        Brisanje svih preuzetih natjecanja
        Sva unesena natjecanja u modulu (Natjecanja) ostat će spremljena
        """
        self.btn_delete_all_help = HoverInfo.create_tooltip(
            widget=self.btn_delete_all,
            text=btn_delete_all_help_text,
            font_size=12,
            anchor="s",
            orientation="right"
        )

        self.btn_create_competition = tk.Button(
            self.frame_buttons,
            text="+",
            font=self.font,
            bg="lime",
            fg="black",
            command=lambda: self.create_new_competition()
        )
        btn_create_competition_help_text = """Spremi označeno natjecanju u modul (Natjecanja)"""
        self.btn_create_competition_help = HoverInfo.create_tooltip(
            widget=self.btn_create_competition,
            text=btn_create_competition_help_text,
            font_size=12,
            anchor="s",
            orientation="left"
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=15, uniform="rows")

        for x in range(0, 10, 1):
            self.frame_buttons.columnconfigure(x, weight=1, uniform="cols")
        self.frame_buttons.rowconfigure(0, weight=1)

        self.frame_tree.grid(row=1, column=0, sticky="nsew")
        self.frame_buttons.grid(row=0, column=0, sticky="nsew")

        self.btn_download_new.grid(row=0, column=0, sticky="nsew")
        self.btn_delete_all.grid(row=0, column=2, sticky="nsew")

        self.btn_create_competition.grid(row=0, column=9, sticky="nsew")

        self.menu.add_command(label="Dodaj", command=lambda: self.create_new_competition())

        self.frame_tree.assign_menu(self.menu)

        #self.preview_competitions()

    def delete_all(self):
        if messagebox.askyesno(
            parent=self,
            title="Brisanje natjecana",
            message="Jeste li sigurni da želite obrisati sva preuzeta natjecanja?\n"
                    "(spremljena natjecanja u modulu 'Natjecanja' neće biti obrisana)"
        ):
            DBRemover.delete_all_downloaded_hss_natjecanja()

    def create_new_competition(self):
        values = self.frame_tree.get_values_of_selected_row()
        if values:
            competition_info: sqlTypes.CompetitionInfo = {
                "Naziv": values["Naziv"].strip(),
                "Datum": Tools.croatian_date_format_to_SQL(values["Datum"]),
                "Mjesto": values["Mjesto"].strip(),
                "Program": "",
                "Adresa": "",
                "Napomena": "",
                "Kategorija": 0,
                "id": 0,
                "hss_id": int(values["hss_id"])
            }
            CompetitionsInput(self, values=competition_info, save=True).wait_window()
        if int(values['hss_id']) in DBGetter.get_hss_ids_of_competitions():
            values["Unešeno"] = self.selected_symbol
            self.frame_tree.update_selected_row(values=values)

    def new_thread(self):
        th = threading.Thread(target=lambda: self.download_competitions())
        th.start()

    def download_competitions(self, check_all: bool = False):
        self.configure(cursor="watch")
        competitions = DBGetter.get_hss_natjecanja()

        # extract ids from list of competition dicts

        if not competitions:
            if not messagebox.askyesno(
                parent=self,
                title="Preuzimanje natjecanja",
                message="Nisu otkrivena natjecanja u memoriji. \nPrvo pokretanje preuzimanja natjecanja može potrajati par minuta.\nNastaviti?"
            ):
                self.configure(cursor="")
                return

        competitions_hss_ids = [int(c['hss_id']) for c in competitions]

        if check_all or not competitions:  # starting year is 2015 because no competitions on the webpage exist with the date of < 2015
            utc_start = Calendar.Calendar.get_month_start(year=2015, month=1)
        else:
            utc_start = competitions[-1]['utc_start'] - Calendar.Calendar.get_utc_milliseconds_in_days(30)

        new_competitions = Downloader.get_competitions(
            utc_start=utc_start,
            utc_end=int(datetime.datetime.now().timestamp()) * 1000 + Calendar.Calendar.get_utc_milliseconds_in_days(30)
        )
        #  remove 'days' from last inserted competition because the competition taking place before the last inserted
        #  can be added after it on the webpage - in 5 years, largest offset was 2 weeks

        logging.info(competitions)

        if not new_competitions:
            messagebox.showinfo(
                parent=self,
                title="Preuzimanje natjecanja",
                message="Nisu otkrivena nova natjecanja."
            )
            self.configure(cursor="")
            return

        new_competitions_ids = [int(c['id']) for c in new_competitions]

        if Tools.check_all_elements_contained_in_list1(new_competitions_ids, competitions_hss_ids):
            messagebox.showinfo(
                parent=self,
                title="Preuzimanje natjecanja",
                message="Nisu otkrivena nova natjecanja."
            )
            self.configure(cursor="")
            return

        for c in new_competitions:
            if c['id'] in competitions_hss_ids:
                continue

            DBAdder.add_hss_natjecanje(
                competition_id=c['id'],
                name=c['Naziv'],
                place=c['Mjesto'],
                utc_start=c['utc_start'],
                utc_end=c['utc_end']
            )

            c['hss_id'] = c['id']
            c['Datum'] = Tools.croatian_date_from_utc_milliseconds(int(c['utc_start']))
            c['Unešeno'] = ""

            self.frame_tree.AddResultToTree(c, True)

        self.preview_competitions()
        self.configure(cursor="")

    def preview_competitions(self):
        self.frame_tree.ClearTree()

        competitions = sorted(DBGetter.get_hss_natjecanja(), key=lambda x: x['hss_id'], reverse=True)

        competitions_hss_ids = DBGetter.get_hss_ids_of_competitions()
        for c in competitions:
            c["Unešeno"] = self.selected_symbol if c['hss_id'] in competitions_hss_ids else ''
            c['Datum'] = Tools.croatian_date_from_utc_milliseconds(int(c['utc_start']))
            self.frame_tree.AddResultToTree(c)
        self.frame_tree.keep_aspect_ratio()
        #self.frame_tree.adjust_all_columns_default()
        self.frame_tree.adjust_all_columns_by_text_length()

