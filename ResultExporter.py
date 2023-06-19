import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import messagebox
from typing import List, Dict
import copy

import ExcelTools
import JSONManager
import Tools
import ScrollableFrame
import ResultsFilter
import ApplicationProperties
from CustomWidgets import CustomBox
import Fonts
from dbcommands_rewrite import DBGetter


class ResultExporter(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.results = None
        self.current_active_config = None
        self.config_file_path = ApplicationProperties.LOCATION + "/Config/ResultExporter.json"

        self.config_file = JSONManager.load_json(self.config_file_path)
        self.available_selection = self.config_file["items"]
        self.configurations = self.config_file["configurations"]

        self.font = Fonts.fonts2["Dnevnik"]["exporter"]["font"]  # tkFont.Font(size=14)

        width = 800
        height = 600

        self.geometry("{}x{}".format(width, height))

        self.frame_cbxs = ComboboxStacker(self, self.available_selection)
        self.frame_options = tk.Frame(self)
        self.frame_summary = tk.Frame(self)

        # <GRID> #
        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=3, uniform="rows")
        self.rowconfigure(2, weight=9, uniform="rows")
        self.columnconfigure(0, weight=2, uniform="cols")
        self.columnconfigure(1, weight=1, uniform="cols")

        self.frame_options.rowconfigure(0, weight=1, uniform="options_rows")
        self.frame_options.rowconfigure(1, weight=3, uniform="options_rows")
        self.frame_options.rowconfigure(2, weight=3, uniform="options_rows")
        self.frame_options.rowconfigure(3, weight=1, uniform="options_rows")
        self.frame_options.rowconfigure(4, weight=3, uniform="options_rows")
        self.frame_options.columnconfigure(0, weight=1, uniform="options_columns")
        self.frame_options.columnconfigure(1, weight=3, uniform="options_columns")
        self.frame_options.columnconfigure(2, weight=3, uniform="options_columns")
        self.frame_options.columnconfigure(3, weight=1, uniform="options_columns")

        self.frame_options.grid_propagate(False)
        self.grid_propagate(False)
        # </GRID> #

        self.scr_text_summary_vertical = tk.Scrollbar(
            self.frame_summary,
            orient="vertical"
        )

        self.scr_text_summary_horizontal = tk.Scrollbar(
            self.frame_summary,
            orient="horizontal"
        )

        self.txt_summary = tk.Text(
            self.frame_summary,
            yscrollcommand=self.scr_text_summary_vertical.set,
            xscrollcommand=self.scr_text_summary_horizontal.set
        )
        self.scr_text_summary_horizontal.configure(command=self.txt_summary.xview)
        self.scr_text_summary_vertical.configure(command=self.txt_summary.yview)

        self.btn_load_config = ttk.Button(
            self.frame_options,
            text="Učitaj",
            font=self.font,
            state="disabled",
            command=lambda: self.load_config()
        )

        self.btn_delete_config = ttk.Button(
            self.frame_options,
            text="Obriši konfiguraciju",
            font=self.font,
            bg="red",
            state="disabled",
            command=lambda: self.delete_current_config()
        )

        self.btn_save_new_config = ttk.Button(
            self.frame_options,
            text="Nova konfiguracija",
            font=self.font,
            bg="lime",
            state="disabled",
            command=lambda: self.create_new_config()
        )

        self.btn_results = ttk.Button(
            self.frame_summary,
            font=self.font,
            text="Odaberi rezultate",
            fg="black",
            bg="yellow",
            command=lambda: self.get_results()
        )

        self.btn_save_current_config = ttk.Button(
            self.frame_options,
            text="Spremi promjene",
            font=self.font,
            bg="green",
            state="disabled",
            command=lambda: self.save_current_config()
        )

        self.cbx_configurations = CustomBox(
            self.frame_options,
            font=self.font,
            values=[str(key) for key in self.configurations],
            state="disabled"
        )

        self.btn_done = ttk.Button(
            self,
            font=self.font,
            text="Izvezi",
            bg="deep sky blue",
            fg="black",
            state="disabled",
            command=lambda: self.done()
        )

        self.frame_summary.grid(row=0, rowspan=3, column=1, sticky="nsew")
        self.btn_results.pack(side="top", fill="x")
        self.scr_text_summary_vertical.pack(side="right", fill="y")
        self.scr_text_summary_horizontal.pack(side="bottom", fill="x")
        self.txt_summary.pack(side="left", fill="both", expand=True)

        self.btn_done.grid(row=0, column=0, sticky="nsew")
        self.frame_options.grid(row=1, column=0, sticky="nsew")
        self.frame_cbxs.grid(row=2, column=0, sticky="nsew")

        self.btn_save_new_config.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.btn_delete_config.grid(row=1, column=2, columnspan=2, sticky="nsew")
        self.btn_save_current_config.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.cbx_configurations.grid(row=4, column=1, columnspan=2, sticky="nsew")

        self.cbx_configurations.bind("<<ComboboxSelected>>", self.load_config)

        self.frame_cbxs.disable_adding_columns()
        self.update_idletasks()
        self.frame_cbxs.update()
        self.frame_options.update()
        self.btn_load_config.update()

    def enable_GUI_elements(self):
        self.btn_done.configure(state="normal")
        self.cbx_configurations.configure(state="normal")
        self.btn_save_new_config.configure(state="normal")
        self.btn_save_current_config.configure(state="normal")
        self.cbx_configurations.current(0)
        self.frame_cbxs.enable_adding_columns()
        self.btn_delete_config.configure(state="normal")
        self.update_idletasks()
        self.load_config()
        self.frame_cbxs.update_idletasks()  # shouldn't be here

    def get_results(self):
        treefilter = ResultsFilter.FilterTreeview(self, False, window_title="Filter za izvoz")
        treefilter.focus()
        treefilter.wait_window()
        if treefilter.user_closed:
            self.destroy()
            return

        shooter_ids = [value for key, value in treefilter.active_shooters.items()] if treefilter.active_shooters else None
        date_to = treefilter.date["to"]
        date_from = treefilter.date["from"]
        competition_ids = [value for key, value in treefilter.active_competitions.items()] if treefilter.active_competitions else None
        programs = [value for key, value in treefilter.active_programs.items()] if treefilter.active_programs else None
        targets = [value for key, value in treefilter.active_targets.items()] if treefilter.active_targets else None
        disciplines = [value for key, value in treefilter.active_disciplines.items()] if treefilter.active_disciplines else None

        self.results = DBGetter.get_results(
            date_from=date_from,
            date_to=date_to,
            shooter_ids=shooter_ids,
            competition_ids=competition_ids,
            programs=programs,
            targets=targets,
            disciplines=disciplines
        )
        summary = "STRIJELCI: \n\n"
        if shooter_ids is None:
            summary += "    SVI\n"
        for shooter_id in shooter_ids:
            shooter = DBGetter.get_shooter_basic_info(shooter_id)
            summary += "    " + shooter["Ime"] + " " + shooter["Prezime"] + "\n"
        summary += f"\n\nDATUM: \n\n    Od: {Tools.SQL_date_format_to_croatian(date_from)}\n    Do: {Tools.SQL_date_format_to_croatian(date_to)} \n"

        summary += "\n\nDISCIPLINE: \n\n"
        if disciplines is None:
            summary += "    SVE\n"
        else:
            for discipline_id in disciplines:
                summary += f"    {DBGetter.get_discipline_details(discipline_id)['Naziv']} \n"
        summary += "\n\nPROGRAMI: \n\n"
        if programs is None:
            summary += "    SVI\n"
        else:
            for program_id in programs:
                summary += f"     {DBGetter.get_program_details(program_id)['Naziv']} \n"
        summary += "\n\nMETE: \n\n"
        if targets is None:
            summary += "    SVE\n"
        else:
            for target_id in targets:
                summary += f"     {DBGetter.get_target_details(target_id)['Naziv']} \n"
        summary += "\n\nNATJECANJA: \n\n"
        if competition_ids is None:
            summary += "    SVA\n"
        else:
            for competition_id in competition_ids:
                competition = DBGetter.get_competition_details(competition_id)
                summary += f"    {'(' + Tools.SQL_date_format_to_croatian(competition['Datum']) + ')'}  {competition['Naziv']} \n"
        self.txt_summary.delete('1.0', tk.END)
        self.txt_summary.insert(tk.END, summary)
        self.enable_GUI_elements()

    def check_configuration_change(self):
        if self.current_active_config is None:
            return False
        if self.configurations[self.current_active_config] == self.remove_blanks_from_config(self.frame_cbxs.get_current_configuration()):
            return False
        return True

    def done(self):
        if self.check_configuration_change():
            ask = messagebox.askyesno("Spremi promjene",
                                    f"Želite li spremiti promjene u '{self.current_active_config}'?")
            if ask:
                self.save_current_config()
        if ExcelTools.write_dictionaries_to_excel(self.results, "Dnevnik", self.frame_cbxs.get_current_configuration()):
            messagebox.showinfo("Izvoz", "Dnevnik je uspješno izvezen kao .xlsx!")
        else:
            messagebox.showerror("Greška", "Došlo je do greške prilikom izvoza datoteke!")
        self.destroy()

    def configuration_exists(self, config_name):
        if config_name in self.configurations:
            return True
        return False

    def refresh_cbx_items(self):
        self.cbx_configurations.configure(values=[str(key) for key in self.configurations])

    def remove_blanks_from_config(self, config):
        cconfig = copy.deepcopy(config)
        for key, value in cconfig.items():
            if key == "" or key is None:
                cconfig.pop(key)
                continue
            if value == "" or value is None:
                cconfig.pop(key)
        return cconfig

    def create_new_config(self):
        ask = FileTitle(self, "Ime konfiguracije")
        ask.focus()
        ask.wait_window()
        if ask.value is not None:
            if self.configuration_exists(ask.value):
                return

            self.configurations[ask.value] = {}

            JSONManager.save_json(self.config_file_path, self.config_file)

            self.refresh_cbx_items()
            self.cbx_configurations.set(ask.value)
            self.load_config()

    def delete_current_config(self):
        current_config = self.cbx_configurations.get()
        try:
            self.configurations.pop(current_config)
        except KeyError:
            pass
        JSONManager.save_json(self.config_file_path, self.config_file)
        self.frame_cbxs.remove_cbxs()
        self.cbx_configurations.set("Izaberite konfiguraciju")

    def save_current_config(self):
        prepared_config = self.remove_blanks_from_config(self.frame_cbxs.get_current_configuration())
        self.configurations[self.cbx_configurations.get()] = prepared_config  # self.frame_cbxs.get_current_configuration()
        JSONManager.save_json(self.config_file_path, self.config_file)

    def load_config(self, event=None):
        if self.check_configuration_change():
            ask = messagebox.askyesno("Spremi promjene", f"Želite li spremiti promjene u '{self.current_active_config}'?")
            if ask:
                self.save_current_config()
        if self.cbx_configurations.get() in self.configurations:
            self.current_active_config = self.cbx_configurations.get()
            self.frame_cbxs.new_cbx_configuration(self.configurations[self.current_active_config])
    

class ComboboxStacker(tk.Frame):  # no idea on the naming
    def __init__(self, parent, combobox_items: List):
        tk.Frame.__init__(self, parent)
        
        self.controller = parent
        self.row = 0
        
        self.style = ttk.Style()
        self.style.configure("ComboboxStacker.TCheckbutton", font=("Arial", 15))
        
        self.combobox_items = combobox_items
        self.cbx_columns_values = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                                   "R", "S", "T", "W", "V", "Z"]
        self.cbx_columns = []
        self.cbxs = []
        self.lbls = []
        self.btns = []
        self.font = Fonts.fonts2["Dnevnik"]["exporter"]["font"]  # tkFont.Font(size=24)
        
        self.frame_main = ScrollableFrame.Vertical(self)
        self.frame_main.grid_propagate(False)

        self.frame_main.scrollable_frame.grid_columnconfigure(0, weight=1, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(1, weight=4, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(2, weight=1, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(3, weight=12, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(4, weight=1, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(5, weight=2, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_columnconfigure(6, weight=1, uniform="stacker_columns")
        self.frame_main.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.pack_propagate(False)

        self.btn_add = ttk.Button(
            self,
            text="Dodaj stupac",
            bg="lime",
            font=self.font,
            command=lambda: self.add_cbx_pair()
        )

        self.frame_main.pack(side="top", expand=True, fill="both")
        self.btn_add.pack(side="bottom")

    def add_empty_lbl(self):
        lbl = tk.Label(  # used as an empty space between comboboxes
            self.frame_main.scrollable_frame,
            text="",
            font=("Arial", 5)
        )
        self.lbls.append(lbl)
        self.lbls[-1].grid(row=self.row, column=0, sticky="nsew")
        self.row += 1
        return self.lbls[-1]

    def add_cbx_pair(self, column=None, value=None):
        lbl = self.add_empty_lbl()
        cbx_column = CustomBox(
            self.frame_main.scrollable_frame,
            font=self.font,
            state="readonly",
            values=self.cbx_columns_values
        )
        self.cbx_columns.append(cbx_column)
        self.cbx_columns[-1].bind("<<ComboboxSelected>>", self.update_available_columns)
        if column is not None:
            self.cbx_columns[-1].set(column)
        cbx_value = CustomBox(
            self.frame_main.scrollable_frame,
            font=self.font,
            state="readonly",
            values=self.combobox_items
        )
        self.cbxs.append(cbx_value)
        if value is not None:
            self.cbxs[-1].set(value)
        self.cbx_columns[-1].grid(row=self.row, column=1, sticky="nsew")
        self.cbxs[-1].grid(row=self.row, column=3, sticky="nsew")

        btn = ttk.Button(
            self.frame_main.scrollable_frame,
            font=self.font,
            text="X",
            bg="red",
            fg="black"
        )
        self.btns.append(btn)
        self.btns[-1].configure(
            command=lambda value_cbx=self.cbxs[-1],
            column_cbx=self.cbx_columns[-1],
            btn=self.btns[-1],
            lbl=lbl: self.remove_row(column_cbx, value_cbx, btn, lbl)
        )
        self.btns[-1].grid(row=self.row, column=5, sticky="nsew")

        self.row += 1

        self.update_available_columns()

    def enable_adding_columns(self):
        self.btn_add.configure(state="normal")
        self.btn_add.update_idletasks()
        self.btn_add.configure(bg="lime")

    def disable_adding_columns(self):
        self.btn_add.configure(state="disabled")

    def remove_row(self, column_cbx, value_cbx, btn, lbl):
        self.cbxs.remove(value_cbx)
        self.cbx_columns.remove(column_cbx)
        self.btns.remove(btn)
        self.lbls.remove(lbl)
        column_cbx.destroy()
        value_cbx.destroy()
        btn.destroy()
        lbl.destroy()
        self.update_available_columns()

    def update_available_columns(self, event=None):
        values = self.available_row_values()
        for cbx in self.cbx_columns:
            cbx.configure(values=values)

    def available_row_values(self):
        temp_values = copy.deepcopy(self.cbx_columns_values)
        for cbx in self.cbx_columns:
            if not cbx.get():
                continue
            temp_values.remove(str(cbx.get()))
        return temp_values

    def remove_cbxs(self):
        for cbx in self.cbxs:
            cbx.destroy()
        for cbx in self.cbx_columns:
            cbx.destroy()
        for lbl in self.lbls:
            lbl.destroy()
        for btn in self.btns:
            btn.destroy()
        self.cbxs = []
        self.cbx_columns = []
        self.lbls = []
        self.btns = []
        self.row = 0

    def new_cbx_configuration(self, cbx_config):
        self.remove_cbxs()
        sorted_cbx_config = copy.deepcopy(cbx_config)
        sorted_cbx_config = dict(sorted(sorted_cbx_config.items(), key=lambda item: item[1]))
        for key, value in sorted_cbx_config.items():
            self.add_cbx_pair(value, key)

    def refresh_combobox_items(self, combobox_items):
        self.combobox_items = combobox_items
        for cbx in self.cbxs:
            cbx.configure(values=self.combobox_items)

    def get_current_configuration(self) -> Dict[str, str]:
        current_config = {}
        for i in range(0, len(self.cbxs), 1):
            current_config[self.cbxs[i].get()] = self.cbx_columns[i].get()
        return current_config


class FileTitle(tk.Toplevel):
    def __init__(self, parent, title):
        tk.Toplevel.__init__(self, parent)
        self.title(title)
        self.font = tkFont.Font(size=14)

        self.value = None

        x = 300
        y = 100

        self.geometry("{}x{}".format(x, y))

        self.ent_title = tk.Entry(
            self,
            font=self.font
        )

        self.btn_save = ttk.Button(
            self,
            bg="lime",
            fg="black",
            text="Spremi",
            font=self.font,
            command=lambda: self.save()
        )

        self.rowconfigure(0, weight=2, uniform="filetitle_rows")
        self.rowconfigure(1, weight=1, uniform="filetitle_rows")

        self.columnconfigure(0, weight=1)

        self.ent_title.grid(row=0, column=0, sticky="nsew")
        self.btn_save.grid(row=1, column=1)

    def save(self):
        if self.ent_title.get():
            self.value = self.ent_title.get()
        self.destroy()
