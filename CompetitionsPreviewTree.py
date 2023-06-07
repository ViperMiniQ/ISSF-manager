import tkinter as tk
from ResultsTree import ResultsTree
import Fonts
import CompetitionsTools


class CompetitionsTree(ResultsTree):
    def __init__(self, parent, controller, columns_dict, column_widths_dict, column_types_dict, style: str, font):
        ResultsTree.__init__(self, parent, controller, columns_dict, column_widths_dict, column_types_dict, style, font)

        self.menu = tk.Menu(self, font=Fonts.fonts2["Competitions"]["treeview"]["font"], tearoff=0)
        self.menu.add_command(label="Dodaj startne liste", command=lambda: self.add_startne_liste())
        self.menu.add_command(label="Prikaži startne liste", command=lambda: self.show_startne_liste())
        self.menu.add_command(label="Ukloni startne liste", command=lambda: self.delete_startne_liste())
        self.menu.add_command(label="(*eksp) Preuzmi startne liste", command=lambda: self.experimental_download_startne_liste(), foreground="deep sky blue")
        self.menu.add_separator()
        self.menu.add_command(label="Dodaj pozivno pismo", command=lambda: self.add_pozivno_pismo())
        self.menu.add_command(label="Prikaži pozivno pismo", command=lambda: self.show_pozivno_pismo())
        self.menu.add_command(label="Ukloni pozivno pismo", command=lambda: self.delete_pozivno_pismo())
        self.menu.add_command(label="(*eksp) Preuzmi pozivno pismo", command=lambda: self.experimental_download_pozivno_pismo(), foreground="deep sky blue")
        self.menu.add_separator()
        self.menu.add_command(label="Dodaj bilten", command=lambda: self.add_bilten())
        self.menu.add_command(label="Prikaži bilten", command=lambda: self.show_bilten())
        self.menu.add_command(label="Ukloni bilten", command=lambda: self.delete_bilten())
        self.menu.add_command(label="(*eksp) Preuzmi bilten", command=lambda: self.experimantal_download_bilten(), foreground="deep sky blue")
        self.assign_menu(self.menu)

    def add_startne_liste(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.add_startne_liste(self, values['id'])

    def add_pozivno_pismo(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.add_pozivno_pismo(self, values['id'])

    def add_bilten(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.add_bilten(self, values['id'])

    def delete_bilten(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.remove_bilten(values['id'])

    def delete_startne_liste(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.remove_startne_liste(values['id'])

    def delete_pozivno_pismo(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.remove_pozivno_pismo(values['id'])

    def experimantal_download_bilten(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.experimental_download_bilten(values['id'])

    def experimental_download_startne_liste(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.experimental_download_startne_liste(values['id'])

    def experimental_download_pozivno_pismo(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.experimental_download_pozivno_pismo(values['id'])

    def show_bilten(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.show_bilten(values['id'])

    def show_startne_liste(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.show_startne_liste(values['id'])

    def show_pozivno_pismo(self):
        values = self.get_values_of_selected_row()
        if values:
            CompetitionsTools.show_pozivno_pismo(values['id'])

    def get_competition_id(self):
        values = self.get_values_of_selected_row()
        return values['id']
