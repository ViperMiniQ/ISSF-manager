import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import HoverInfo
import Colors
from ResultsInput import ResultsInput
from ResultsAdditional import ResultsAdditional
from ResultsTree import ResultsTree
from ResultsFilter import FilterTreeview
from NoteWindow import NoteWindow
import Tools
import sqlTypes
from Logger import benchmark
import Changes
import KeepAspectRatio
import Fonts
from dbcommands_rewrite import DBGetter, DBAdder, DBRemover, DBUpdate


class Results(tk.Frame):
    @benchmark
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.showing_input = True

        self.pan = ttk.PanedWindow(self, orient=tk.VERTICAL)

        Changes.subscribe_to_shooters(self)
        Changes.subscribe_to_targets(self)
        Changes.subscribe_to_disciplines(self)
        Changes.subscribe_to_programs(self)
        Changes.subscribe_to_competitions(self)

        self.competitions = {}
        self.shooters = {}
        self.disciplines = []
        self.programs = []
        self.targets = []
        self.update_excel = 0
        self.updating_result = False
        self.updating_result_id = 0
        self.tree_edit_item = 0

        self.treeview_columns_dict = {
            "Strijelac": 1,
            "Disciplina": 1,
            "Program": 1,
            "Meta": 1,
            "P": 1,
            "R10": 1,
            "R20": 1,
            "R30": 1,
            "R40": 1,
            "R50": 1,
            "R60": 1,
            "Ineri": 1,
            "Datum": 1,
            "Rezultat": 1,
            "Natjecanje": 0,
            "id": 0,
            "Napomena": 0
        }

        self.treeview_column_widths = {
            "Strijelac": 125,
            "Disciplina": 75,
            "Program": 60,
            "Meta": 60,
            "P": 20,
            "R10": 40,
            "R20": 40,
            "R30": 40,
            "R40": 40,
            "R50": 40,
            "R60": 40,
            "Ineri": 20,
            "Datum": 85,
            "Rezultat": 65,
            "Natjecanje": 85,
            "id": 1,
            "Napomena": 15
        }

        # types needed for sorting operation, treeview only accepts string
        self.treeview_column_types = {
            "Strijelac": "str",
            "Disciplina": "str",
            "Program": "str",
            "Meta": "str",
            "P": "int",
            "R10": "float",
            "R20": "float",
            "R30": "float",
            "R40": "float",
            "R50": "float",
            "R60": "float",
            "Ineri": "int",
            "Datum": "date",
            "Rezultat": "float",
            "Natjecanje": "str",
            "id": "int",
            "Napomena": "str"
        }

        self.frame_input = ResultsInput(self.pan, self)
        self.frame_tree = ResultsTree(self.pan, self, self.treeview_columns_dict,
                                      self.treeview_column_widths,
                                      self.treeview_column_types, "ResultsTree",
                                      Fonts.fonts2["Dnevnik"]["treeview"]["font"]
        )
        self.frame_tree.set_colors(
            odd_row_bg=Colors.colors["Results"]["treeview"]["odd_rows"]["bg"],
            even_row_bg=Colors.colors["Results"]["treeview"]["even_rows"]["bg"],
            odd_row_fg=Colors.colors["Results"]["treeview"]["odd_rows"]["fg"],
            even_row_fg=Colors.colors["Results"]["treeview"]["even_rows"]["fg"]
        )
        KeepAspectRatio.subscribe(self.frame_tree)
        self.frame_additional = ResultsAdditional(self.pan, self, tree=self.frame_tree, input_frame=self.frame_input)

        self.frame_tree.pack_propagate(False)
        self.frame_input.grid_propagate(False)
        self.frame_input.pack_propagate(False)

        self.pack_propagate(False)

        self.pan.add(self.frame_input, weight=2)
        self.pan.add(self.frame_tree, weight=10)
        self.pan.add(self.frame_additional, weight=1)

        self.pan.pack(expand=True, fill="both")

        self.frame_input.clear_entries()
        self.frame_tree.ClearTree()

        self.update_all()

        self.ReloadAllResultsAddToTree()

        self.tooltip = HoverInfo.BaseTooltip(self, 14)

        self.frame_tree.tree_shooter.bind("<Motion>", self.show_row_tooltip)

        self.bind("<Leave>", lambda event: self.tooltip.hidetip())
        self.update_idletasks()
        self.update()

    def show_row_tooltip(self, event=None):
        self.tooltip.hidetip()
        try:
            selected_row = self.frame_tree.tree_shooter.identify_row(event.y)
            values = self.frame_tree.tree_shooter.set(selected_row)
            note_text = DBGetter.get_result_note_text(values["id"])
            if note_text is None or note_text == "":
                return
            self.tooltip.showtip(event.x_root + 10, event.y_root + 5, note_text)
        except KeyError:  # happens on hover over columns
            self.tooltip.hidetip()

    def change_input_visibility(self):
        if self.showing_input:
            self.hide_input()
            self.showing_input = False
        else:
            self.show_input()
            self.showing_input = True

    def hide_input(self):
        self.frame_input.grid_forget()
        self.frame_tree.grid(row=0, rowspan=2, sticky="nsew")

    def show_input(self):
        self.frame_tree.grid_forget()
        self.frame_input.grid(row=0, column=0, sticky="nsew")
        self.frame_tree.grid(row=1, column=0, sticky="nsew")

    def FilterTree(self, results=None):
        if not results:
            treefilter = FilterTreeview(self, False)
            treefilter.wait_window()
            if treefilter.user_closed:
                return
            results = DBGetter.get_results(
                date_from=treefilter.date["from"],
                date_to=treefilter.date["to"],
                shooter_ids=[value for key, value in treefilter.active_shooters.items()] if treefilter.active_shooters else None,
                competition_ids=[value for key, value in treefilter.active_competitions.items()] if treefilter.active_competitions else None,
                programs=[value for key, value in treefilter.active_programs.items()] if treefilter.active_programs else None,
                targets=[value for key, value in treefilter.active_targets.items()] if treefilter.active_targets else None,
                disciplines=[value for key, value in treefilter.active_disciplines.items()] if treefilter.active_disciplines else None
            )
        self.frame_tree.ClearTree()
        for result in results:
            result["Datum"] = Tools.SQL_date_format_to_croatian(result["Datum"])
            if result["Napomena"] != "" and result["Napomena"] is not None:
                result["Napomena"] = "*"
            else:
                result["Napomena"] = ""
            self.frame_tree.AddResultToTree(result, top=False)

    
    def ClearTree(self):
        self.frame_tree.ClearTree()

    def DeleteRecordIndb(self, record_id):
        DBRemover.delete_result(record_id)
    
    def DeletePressed(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        if not messagebox.askyesno("Obriši zapis", "Jeste li sigurni da želite obrisati označeni zapis?"):
            return

        self.DeleteRecordIndb(values["id"])
        self.frame_tree.DeleteTreeRow("selected")

    def EditPressed(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return

        self.updating_result = True
        self.updating_result_id = values["id"]
        self.tree_edit_item = values["rowID"]

        self.frame_input.clear_entries()
        self.frame_input.SetShooter(values["Strijelac"])
        self.frame_input.SetDate(datetime.datetime.strptime(values["Datum"], Tools.croatian_date_format))
        self.frame_input.SetDiscipline(values["Disciplina"])
        self.frame_input.SetProgram(values["Program"])
        self.frame_input.SetTarget(values["Meta"])
        self.frame_input.SetCompetition(values["Natjecanje"])
        self.frame_input.SetP(values["P"])
        self.frame_input.SetR10(values["R10"])
        self.frame_input.SetR20(values["R20"])
        self.frame_input.SetR30(values["R30"])
        self.frame_input.SetR40(values["R40"])
        self.frame_input.SetR50(values["R50"])
        self.frame_input.SetR60(values["R60"])
        self.frame_input.SetNote(DBGetter.get_result_note_text(values["id"]))

        self.frame_input.SetBtnAddTitle("Osvježi")  # add text, not title

    def FilterPressed(self):
        self.FilterTree()

    def RefreshPressed(self):
        self.ReloadAllResultsAddToTree()

    def ReloadAllResultsAddToTree(self):
        self.frame_tree.ClearTree()
        results = DBGetter.get_results()
        for result in results:
            result["Datum"] = Tools.SQL_date_format_to_croatian(result["Datum"])
            if result["Napomena"] != "" and result["Napomena"] is not None:
                result["Napomena"] = "*"
            else:
                result["Napomena"] = ""
            self.frame_tree.AddResultToTree(result, top=False)

    def GetCompetitionIdFromName(self, competition: str):
        for c in self.competitions:
            if f"({Tools.SQL_date_format_to_croatian(c['Datum'])}) {c['Naziv']}" == competition:
                return c["id"]

    def GetShooterIdFromName(self, shooter: str):
        for s in self.shooters:
            if s["Ime"] + " " + s["Prezime"] == shooter:
                return s["id"]

    def GetDisciplineIdFromName(self, discipline: str):
        for d in self.disciplines:
            if d["Naziv"] == discipline:
                return d["id"]

    def GetTargetIdFromName(self, target: str):
        for t in self.targets:
            if t["Naziv"] == target:
                return t["id"]

    def GetProgramIdFromName(self, program: str):
        for p in self.programs:
            if p["Naziv"] == program:
                return p["id"]

    def AddButtonPressed(self):
        input_values = self.frame_input.GetEntryValues()

        if not input_values["Strijelac"]:
            messagebox.showerror("Greška", "Nije odabran ispravan strijelac!")
            return

        if not input_values["Disciplina"]:
            messagebox.showerror("Greška", "Nije odabrana valjana disciplina!")
            return

        if not input_values["Program"]:
            messagebox.showerror("Greška", "Nije odabran valjani program!")
            return

        if not input_values["Meta"]:
            messagebox.showerror("Greška", "Nije odabrana valjana meta!")
            return

        if not input_values["Natjecanje"]:
            messagebox.showerror("Greška", "Nije odabrano valjano natjecanje!")
            return

        input_values["idNatjecanja"] = self.GetCompetitionIdFromName(input_values["Natjecanje"])
        input_values["idStrijelac"] = self.GetShooterIdFromName(input_values["Strijelac"])
        p = input_values["Program"]
        d = input_values["Disciplina"]
        m = input_values["Meta"]
        input_values["Program"] = self.GetProgramIdFromName(input_values["Program"])
        input_values["Disciplina"] = self.GetDisciplineIdFromName(input_values["Disciplina"])
        input_values["Meta"] = self.GetTargetIdFromName(input_values["Meta"])

        if self.updating_result:
            self.frame_input.SetBtnAddTitle("Dodaj")

            self.UpdateShooterdb(input_values, self.updating_result_id)

            if input_values != "":
                input_values["Napomena"] = "*"
            else:
                input_values["Napomena"] = ""

            input_values["Datum"] = Tools.SQL_date_format_to_croatian(str(input_values["Datum"]))
            input_values["id"] = self.updating_result_id
            input_values["Program"] = p
            input_values["Disciplina"] = d
            input_values["Meta"] = m
            self.frame_tree.EditTreeviewRowValues(self.tree_edit_item, input_values)

            self.tree_edit_item = None
            self.updating_result_id = 0
            self.updating_result = False
        else:
            self.UpdatedbDnevnik(input_values)

            last_rowid = DBGetter.get_last_result_id()
            input_values["id"] = last_rowid
            input_values["Datum"] = Tools.SQL_date_format_to_croatian(str(input_values["Datum"]))

            if input_values != "":
                input_values["Napomena"] = "*"
            else:
                input_values["Napomena"] = ""
            input_values["Program"] = p
            input_values["Disciplina"] = d
            input_values["Meta"] = m
            print(input_values)
            self.frame_tree.AddResultToTree(input_values, top=True)

        self.frame_input.clear_entries()

    
    def BindI(self):
        values = self.frame_tree.get_values_of_selected_row()
        note_text = DBGetter.get_result_note_text(values["id"])
        if not (note_text is None or note_text == ""):
            show_note = NoteWindow(self, text=note_text)
            show_note.focus()
            show_note.wait_window()

    def ClearButtonPressed(self):
        self.frame_input.clear_entries()
        self.frame_input.SetBtnAddTitle("Dodaj")
        self.updating_result = False

    def AdjustColumnsSizePressed(self):
        self.frame_tree.adjust_all_columns_by_text_length()

    def update_shooters(self):
        self.shooters = DBGetter.get_active_shooters()
        shooters = [shooter["Ime"] + " " + shooter["Prezime"] for shooter in self.shooters]
        self.frame_input.UpdateShootersList(shooters)

    def update_programs(self):
        self.programs = DBGetter.get_active_programs()
        programs = [program["Naziv"] for program in self.programs]
        self.frame_input.UpdateProgramsList(programs)

    def update_targets(self):
        self.targets = DBGetter.get_active_targets()
        targets = [target["Naziv"] for target in self.targets]
        self.frame_input.UpdateTargetsList(targets)

    def update_disciplines(self):
        self.disciplines = DBGetter.get_active_disciplines()
        disciplines = [discipline["Naziv"] for discipline in self.disciplines]
        self.frame_input.UpdateDisciplinesList(disciplines)

    def update_competitions(self):
        self.competitions = DBGetter.get_active_competitions()
        competitions = [f"({Tools.SQL_date_format_to_croatian(competition['Datum'])}) {competition['Naziv']}"
                        for competition in self.competitions]
        self.frame_input.UpdateCompetitionsList(competitions)

    def update_all(self):
        self.update_shooters()
        self.update_programs()
        self.update_competitions()
        self.update_targets()
        self.update_disciplines()

    def UpdateTreeviewDispayColumns(self):
        self.frame_tree.SelectColumnsToDisplay()
        self.frame_tree.adjust_all_columns_by_text_length()

    def UpdateShooterdb(self, result: sqlTypes.ResultInput, result_id: int):
        DBUpdate.update_result(result, result_id)

    def UpdatedbDnevnik(self, values: sqlTypes.ResultInput):
        DBAdder.add_result(values)
