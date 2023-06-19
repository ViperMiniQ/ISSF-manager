import shutil
import tkinter as tk
from typing import List
import tkinter.font as tkFont
from tkinter import messagebox, filedialog
import Colors
import ScrollableFrame
from Logger import benchmark
import ShowShooters
import Tools
import CompetitionsInput
import sqlTypes
import copy
import Changes
import Fonts
import ApplicationProperties
from dbcommands_rewrite import DBGetter, DBRemover, DBAdder
import CompetitionsTools
import KeepAspectRatio


class CompetitionPreview(tk.Frame):
    bilten_path = "/Data/Bilteni/"
    startne_liste_path = "/Data/Startne liste/"
    pozivno_pismo_path = "/Data/Pozivno pismo/"

    @benchmark
    def __init__(self, master, controller, values: sqlTypes.CompetitionInfo):
        tk.Frame.__init__(self, master, width=10, height=245, relief="raised", bd=7)
        self.master = master
        self.values = copy.deepcopy(values)
        self.competition_id = self.values["id"]
        self.controller = controller

        KeepAspectRatio.subscribe(self)
        Colors.subscribe(self)

        self.title = tk.StringVar()
        self.type = tk.StringVar()
        self.address = tk.StringVar()
        self.location = tk.StringVar()
        self.lbl_categories_text = tk.StringVar()
        self.address_and_location = tk.StringVar()
        self.additional = tk.StringVar()
        self.date = tk.StringVar()
        self.hss_id = tk.StringVar()

        self.load_information()

        self.rifle_shooters = []
        self.pistol_shooters = []
        self.font = Fonts.fonts2["Competitions"]["preview"]["font"]
        self.x = 800
        self.max_shooters = 0
        self.y_row = 35
        self.additional_weight = self.additional.get().count("\n") + 1

        self.grid_propagate(False)

        #   Naziv                                                                           KAD | JUN | SEN | VET
        #                                                   ISSF
        #
        #                   Pištolj: |+|                                    Puška: |+|
        #
        #                        [__________________]                            [_________________]
        #
        #
        #
        #   Adresa, Mjesto
        #
        #   Datum
        #

        self.lbl_title = tk.Label(
            self,
            anchor="w",
            textvariable=self.title,
            font=self.font,
            width=1
        )

        self.lbl_categories = tk.Label(
            self,
            textvariable=self.lbl_categories_text,
            font=self.font,
            anchor="e"
        )

        self.lbl_type = tk.Label(
            self,
            textvariable=self.type,
            font=self.font,
            anchor="center"
        )

        self.lbl_pistol = tk.Label(
            self,
            text="Pištolj:",
            font=self.font
        )

        self.btn_pistol = tk.Button(
            self,
            text="+",
            font=self.font,
            bd=4,
            command=lambda: self.show_available_shooters(0)
        )

        self.lbl_pistol_shooters = tk.Label(
            self,
            font=self.font,
            anchor="center",
            justify="center",
        )

        self.lbl_rifle = tk.Label(
            self,
            text="Puška:",
            font=self.font
        )

        self.btn_rifle = tk.Button(
            self,
            text="+",
            font=self.font,
            bd=4,
            command=lambda: self.show_available_shooters(1)
        )

        self.lbl_rifle_shooters = tk.Label(
            self,
            font=self.font,
            anchor="center",
            justify="center",
        )

        self.lbl_address_and_location = tk.Label(
            self,
            textvariable=self.address_and_location,
            font=self.font,
            anchor="w",
            width=1
        )

        self.lbl_date = tk.Label(
            self,
            textvariable=self.date,
            font=self.font,
            anchor="w",
            width=1
        )

        self.lbl_additional = tk.Label(
            self,
            textvariable=self.additional,
            font=self.font,
            anchor="w",
            justify="left"
        )

        self.lbl_hss_id = tk.Label(
            self,
            textvariable=self.hss_id,
            font=self.font,
            anchor="e",
            justify="right"
        )

        self.btn_delete = tk.Button(
            self,
            text="Obriši",
            fg="white",
            bg="red",
            font=self.font,
            command=lambda: self.delete()
        )

        self.btn_modify = tk.Button(
            self,
            text="Uredi",
            fg="yellow",
            bg="black",
            font=self.font,
            command=lambda: self.modify()
        )

        self.btn_show = tk.Button(
            self,
            text="Rezultati",
            fg="black",
            bg="white",
            font=self.font,
            command=lambda: self.show_results()
        )

        self.btn_bilten = tk.Button(
            self,
            text="Bilten",
            fg="black",
            bg="grey",
            font=self.font,
            command=self.popup_menu_bilten
        )
        self.btn_add_bilten = tk.Button(
            self,
            text="+",
            font=self.font,
            command=self.add_bilten
        )

        self.btn_options = tk.Button(
            self,
            text="---",
            font=self.font,
            command=lambda: self.popup_menu_options()
        )

        self.menu_options = tk.Menu(self.btn_options, font=self.font, tearoff=0)
        self.menu_options.add_command(label="Uredi", command=lambda: self.modify())
        self.menu_options.add_separator()
        self.menu_options.add_command(label="Rezultati", command=lambda: self.show_results())
        self.menu_options.add_separator()
        self.menu_options.add_command(label="Obriši", command=lambda: self.delete(), background="red")

        self.menu_bilten = tk.Menu(self.btn_bilten, font=self.font, tearoff=0, title="Bilten")
        self.menu_bilten.add_command(label="Dodaj", command=lambda: self._add_bilten())
        self.menu_bilten.add_separator()
        self.menu_bilten.add_command(label="Ukloni", command=lambda: self._remove_bilten())
        self.menu_bilten.add_separator()
        self.menu_bilten.add_command(
            label="Prikaži",
            command=lambda: CompetitionsTools.show_bilten(self.competition_id)
        )
        self.menu_bilten.add_separator()
        self.menu_bilten.add_command(
            label="(*eksp) Preuzmi",
            command=lambda: self._experimental_download_bilten(),
            foreground="deep sky blue"
        )

        self.btn_startne_liste = tk.Button(
            self,
            text="Startne liste",
            fg="black",
            bg="grey",
            font=self.font,
            command=self.popup_menu_startne_liste
        )
        self.btn_add_startne_liste = tk.Button(
            self,
            text="+",
            font=self.font,
            command=self.add_startne_liste
        )

        self.menu_startne_liste = tk.Menu(self.btn_startne_liste, font=self.font, tearoff=0, title="Startne liste")
        self.menu_startne_liste.add_command(label="Dodaj", command=lambda: self._add_startne_liste())
        self.menu_startne_liste.add_separator()
        self.menu_startne_liste.add_command(label="Ukloni", command=lambda: self._remove_startne_liste())
        self.menu_startne_liste.add_separator()
        self.menu_startne_liste.add_command(
            label="Prikaži",
            command=lambda: CompetitionsTools.show_startne_liste(self.competition_id)
        )
        self.menu_startne_liste.add_separator()
        self.menu_startne_liste.add_command(
            label="(*eksp) Preuzmi",
            command=lambda: self._experimental_download_startne_liste(),
            foreground="deep sky blue"
        )

        self.btn_pozivno_pismo = tk.Button(
            self,
            text="Pozivno pismo",
            fg="black",
            bg="grey",
            font=self.font,
            command=self.popup_menu_pozivno_pismo
        )
        self.btn_add_pozivno_pismo = tk.Button(
            self,
            text="+",
            font=self.font,
            command=self.add_pozivno_pismo
        )

        self.menu_pozivno_pismo = tk.Menu(self.btn_pozivno_pismo, font=self.font, tearoff=0, title="Pozivno pismo")
        self.menu_pozivno_pismo.add_command(label="Dodaj", command=lambda: self._add_pozivno_pismo())
        self.menu_pozivno_pismo.add_separator()
        self.menu_pozivno_pismo.add_command(label="Ukloni", command=lambda: self._remove_pozivno_pismo())
        self.menu_pozivno_pismo.add_separator()
        self.menu_pozivno_pismo.add_command(
            label="Prikaži", 
            command=lambda: CompetitionsTools.show_pozivno_pismo(self.competition_id)
        )
        self.menu_pozivno_pismo.add_separator()
        self.menu_pozivno_pismo.add_command(
            label="(*eksp) Preuzmi",
            command=lambda: self._experimental_download_pozivno_pismo(),
            foreground="deep sky blue"
        )

        self.btn_bilten.grid(row=6, column=9, columnspan=2, sticky="nsew")
        self.btn_pozivno_pismo.grid(row=6, column=6, columnspan=2, sticky="nsew")
        self.btn_startne_liste.grid(row=6, column=3, columnspan=2, sticky="nsew")

        self.load_colors()
        for y in range(0, 7, 1):
            self.rowconfigure(y, weight=1, uniform="rows33")

        self.columnconfigure(0, weight=1, uniform="columns33")
        for x in range(1, 15, 1):
            self.columnconfigure(x, weight=3, uniform="columns33")
        self.columnconfigure(15, weight=1, uniform="columns33")

        self.lbl_title.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.lbl_categories.grid(row=0, column=10, columnspan=6, sticky="nsew")
        self.lbl_type.grid(row=1, column=0, columnspan=16, sticky="nsew")
        self.lbl_rifle.grid(row=2, column=2, columnspan=2, sticky="nsew")
        self.btn_rifle.grid(row=2, column=4, sticky="w")
        self.lbl_rifle_shooters.grid(row=3, column=2, columnspan=6, sticky="nsew")
        self.lbl_pistol.grid(row=2, column=9, columnspan=2, sticky="nsew")
        self.btn_pistol.grid(row=2, column=11, sticky="w")
        self.lbl_pistol_shooters.grid(row=3, column=9, columnspan=6, sticky="nsew")
        self.lbl_additional.grid(row=4, column=2, columnspan=13, sticky="nsew")
        self.lbl_address_and_location.grid(row=5, column=1, columnspan=14, sticky="nsew")
        self.lbl_date.grid(row=6, column=0, columnspan=5, sticky="nsew")
        self.lbl_hss_id.grid(row=6, column=14, columnspan=2, sticky="nsew")
        self.btn_options.grid(row=6, column=12, columnspan=1, sticky="nsew")

        self.adjust_row_height(4, self.additional_weight)
        self.adjust_height()
        self.refresh_shooters()

        self.check_bilten_exists()
        self.check_startne_liste_exists()
        self.check_pozivno_pismo_exists()

        self.keep_aspect_ratio()

    def load_colors(self):
        self.set_bg_color(color=self.get_bg_color(self.values['Program']))
        self.set_fg_color(color=self.get_fg_color(self.values['Program']))

    #  raise save error
    @classmethod
    def save_fg_color(cls, program_name: str, color: str):
        try:
            Colors.colors["CompetitionPreview"]["Programs"][program_name]["fg"] = color
        except KeyError:
            pass

    @classmethod
    def save_bg_color(cls, program_name: str, color: str):
        try:
            Colors.colors["CompetitionPreview"]["Programs"][program_name]["bg"] = color
        except KeyError:
            pass

    @classmethod
    def get_fg_color(cls, program_name: str) -> str:
        fg = "black"
        try:
            fg = Colors.colors["CompetitionPreview"]["Programs"][program_name]["fg"]
        except KeyError:
            fg = "black"
        finally:
            return fg

    @classmethod
    def get_bg_color(cls, program_name: str) -> str:
        bg = "white"
        try:
            bg = Colors.colors["CompetitionPreview"]["Programs"][program_name]["bg"]
        except KeyError:
            bg = "white"
        finally:
            return bg

    def check_existence_of_all_files(self):
        self.check_bilten_exists()
        self.check_startne_liste_exists()
        self.check_pozivno_pismo_exists()

    def _remove_bilten(self):
        CompetitionsTools.remove_bilten(self.competition_id)
        self.check_bilten_exists()

    def _remove_startne_liste(self):
        CompetitionsTools.remove_startne_liste(self.competition_id)
        self.check_startne_liste_exists()

    def _remove_pozivno_pismo(self):
        CompetitionsTools.remove_pozivno_pismo(self.competition_id)
        self.check_pozivno_pismo_exists()

    def _experimental_download_bilten(self):
        CompetitionsTools.experimental_download_bilten(self.competition_id)
        self.check_bilten_exists()

    def _experimental_download_startne_liste(self):
        CompetitionsTools.experimental_download_startne_liste(self.competition_id)
        self.check_startne_liste_exists()

    def _experimental_download_pozivno_pismo(self):
        CompetitionsTools.experimental_download_pozivno_pismo(self.competition_id)
        self.check_pozivno_pismo_exists()

    def _add_bilten(self):
        CompetitionsTools.add_bilten(self, self.competition_id)
        self.check_bilten_exists()

    def _add_startne_liste(self):
        CompetitionsTools.add_startne_liste(self, self.competition_id)
        self.check_startne_liste_exists()

    def _add_pozivno_pismo(self):
        CompetitionsTools.add_pozivno_pismo(self, self.competition_id)
        self.check_pozivno_pismo_exists()

    def popup_menu_options(self):
        y = self.btn_options.winfo_rooty() - self.menu_options.winfo_reqheight()
        if y < 0:
            y = self.btn_options.winfo_rooty()
            
        self.menu_options.tk_popup(
            x=self.btn_options.winfo_rootx(),
            y=y,
            entry=0
        )
        self.menu_options.grab_release()

    def popup_menu_startne_liste(self):
        y = self.btn_startne_liste.winfo_rooty() - self.menu_startne_liste.winfo_reqheight()
        if y < 0:
            y = self.btn_startne_liste.winfo_rooty()
            
        self.menu_startne_liste.tk_popup(
            x=self.btn_startne_liste.winfo_rootx(),
            y=y,
            entry=0
        )
        self.menu_startne_liste.grab_release()

    def popup_menu_pozivno_pismo(self):
        y = self.btn_pozivno_pismo.winfo_rooty() - self.menu_pozivno_pismo.winfo_reqheight()
        if y < 0:
            y = self.btn_pozivno_pismo.winfo_rooty()
            
        self.menu_pozivno_pismo.tk_popup(x=self.btn_pozivno_pismo.winfo_rootx(), y=y, entry=0)
        self.menu_pozivno_pismo.grab_release()

    def popup_menu_bilten(self):
        y = self.btn_bilten.winfo_rooty() - self.menu_bilten.winfo_reqheight()
        if y < 0:
            y = self.btn_bilten.winfo_rooty()
            
        self.menu_bilten.tk_popup(x=self.btn_bilten.winfo_rootx(), y=y, entry=0)
        self.menu_bilten.grab_release()

    def check_bilten_exists(self):
        if DBGetter.get_bilten(competition_id=self.competition_id):
            self.btn_bilten.configure(bg="deep sky blue")
            return
        self.btn_bilten.configure(bg="grey")

    def check_startne_liste_exists(self):
        if DBGetter.get_startne_liste(competition_id=self.competition_id):
            self.btn_startne_liste.configure(bg="deep sky blue")
            return
        self.btn_startne_liste.configure(bg="grey")

    def check_pozivno_pismo_exists(self):
        if DBGetter.get_pozivno_pismo(competition_id=self.competition_id):
            self.btn_pozivno_pismo.configure(bg="deep sky blue")
            return
        self.btn_pozivno_pismo.configure(bg="grey")

    def show_results(self):
        self.controller.show_results(self.competition_id)

    def load_information(self):
        self.title.set(self.values["Naziv"])
        self.type.set(self.values["Program"])
        self.address.set(self.values["Adresa"])
        self.location.set(self.values["Mjesto"])
        address_and_location = self.address.get() + ", " + self.location.get() if self.address.get() else self.location.get()
        self.address_and_location.set(address_and_location)
        self.date.set(Tools.SQL_date_format_to_croatian(self.values['Datum']))
        self.additional.set(self.values["Napomena"])
        self.hss_id.set(self.values['hss_id'] if self.values['hss_id'] else '')
        categories_text = ""
        categories = Tools.TranslateCategoriesToList(self.values["Kategorija"])
        for txt in categories:
            categories_text += txt + " | "
        categories_text = categories_text[:-2]
        self.lbl_categories_text.set(categories_text)

    def modify(self):
        info = CompetitionsInput.CompetitionsInput(self, values=self.values, save=True, modify=True)
        info.focus()
        info.wait_window()
        if info.values is not None:
            self.values = info.values
            self.values["id"] = self.competition_id
            self.load_information()
            self.additional_weight = self.additional.get().count("\n") + 1
            self.adjust_height()
            self.update()
            self.keep_aspect_ratio()
            Changes.set_competitions()

    def delete(self):
        if not messagebox.askyesno(
                title="Obriši natjecanje",
                message='Jeste li sigurni da želite obrisati natjecanje "{}"?'.format(self.title.get())
        ):
            return
        
        DBRemover.delete_competition(self.competition_id)
        Changes.set_competitions()
        Changes.call_refresh_competitions()

    def set_fg_color(self, color):
        self.lbl_title.configure(fg=color)
        self.lbl_additional.configure(fg=color)
        self.lbl_type.configure(fg=color)
        self.lbl_rifle_shooters.configure(fg=color)
        self.lbl_rifle.configure(fg=color)
        self.lbl_pistol_shooters.configure(fg=color)
        self.lbl_pistol.configure(fg=color)
        self.lbl_date.configure(fg=color)
        self.lbl_address_and_location.configure(fg=color)
        self.lbl_categories.configure(fg=color)
        self.lbl_hss_id.configure(fg=color)
    
    def set_bg_color(self, color):
        self.lbl_title.configure(bg=color)
        self.lbl_additional.configure(bg=color)
        self.lbl_type.configure(bg=color)
        self.lbl_rifle_shooters.configure(bg=color)
        self.lbl_rifle.configure(bg=color)
        self.lbl_pistol_shooters.configure(bg=color)
        self.lbl_pistol.configure(bg=color)
        self.lbl_date.configure(bg=color)
        self.lbl_address_and_location.configure(bg=color)
        self.lbl_categories.configure(bg=color)
        self.lbl_hss_id.configure(bg=color)

        self.configure(bg=color)

    def adjust_height(self):
        y = self.y_row * (8 + self.max_shooters + self.additional_weight)
        self.configure(height=y)

    def add_shooters(self, rifle, shooters: List[sqlTypes.Shooter]):
        """rifle: 1 if rifle, 0 if pistol"""
        new_text = ""
        adjust_weight = 1

        for shooter in shooters:
            new_text += shooter["Strijelac"] + "\n"
            adjust_weight += 1

        if rifle:
            self.lbl_rifle_shooters.configure(text=new_text)
        else:
            self.lbl_pistol_shooters.configure(text=new_text)

        self.max_shooters = max(self.lbl_rifle_shooters["text"].count('\n'),
                                self.lbl_pistol_shooters["text"].count('\n')) + 1
        self.adjust_height()
        self.adjust_row_height(3, self.max_shooters)

    def add_bilten(self):
        file = filedialog.askopenfilename(parent=self, title="Izaberite datoteku biltena")
        if not file:
            return
        try:
            extension = file.split('.')[-1]
            shutil.copy(
                file,
                ApplicationProperties.LOCATION + self.bilten_path + str(self.competition_id) + "_bilten." + extension
            )
        except shutil.SameFileError:
            tk.messagebox.showerror(
                title="Greška",
                message="Greška u dodavanju biltena, pokušajte pokrenuti program kao administrator."
            )
        self.check_bilten_exists()

    def add_pozivno_pismo(self):
        file = filedialog.askopenfilename(parent=self, title="Izaberite datoteku pozivnog pisma")
        if not file:
            return
        try:
            extension = file.split('.')[-1]
            shutil.copy(
                file,
                ApplicationProperties.LOCATION + self.pozivno_pismo_path
                + str(self.competition_id) + "_pozivno_pismo." + extension
            )
        except shutil.SameFileError:
            tk.messagebox.showerror(
                title="Greška",
                message="Greška u dodavanju pozivnog pisma, pokušajte pokrenuti program kao administrator."
            )
        self.check_pozivno_pismo_exists()

    def add_startne_liste(self):
        file = filedialog.askopenfilename(parent=self, title="Izaberite datoteku startne liste")
        if not file:
            return
        try:
            extension = file.split('.')[-1]
            shutil.copy(
                file,
                ApplicationProperties.LOCATION + self.startne_liste_path
                + str(self.competition_id) + "_startne_liste." + extension
            )
        except shutil.SameFileError:
            tk.messagebox.showerror(
                title="Greška",
                message="Greška u dodavanju startne liste, pokušajte pokrenuti program kao administrator."
            )
        self.check_startne_liste_exists()

    def show_available_shooters(self, rifle):
        """rifle: 1 if rifle, 0 if pistol"""
        shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters()
        select_shooters = {}

        for shooter in shooters:
            name = f"{shooter['Ime']} {shooter['Prezime']}"
            select_shooters[name] = 0

        if rifle:
            window_title = "Za pušku"
            for shooter in self.rifle_shooters:
                select_shooters[shooter["Strijelac"]] = 1
        else:
            window_title = "Za pištolj"
            for shooter in self.pistol_shooters:
                select_shooters[shooter["Strijelac"]] = 1

        ask = ShowShooters.ShowShooters(self, window_title, select_shooters)
        ask.focus()

        ask.wait_window()
        if ask.values is None:
            return

        DBRemover.delete_all_shooters_at_competition(self.competition_id, rifle)

        for shooter in shooters:
            name = f"{shooter['Ime']} {shooter['Prezime']}"
            select_shooters[name] = shooter['id']

        for shooter, on_value in ask.values.items():
            if on_value:
                DBAdder.add_shooter_to_competition(self.competition_id, select_shooters[shooter], rifle)

        self.refresh_shooters()

    def adjust_row_height(self, row, weight):
        self.rowconfigure(row, weight=weight, uniform="rows33")
        self.keep_aspect_ratio()

    def refresh_pistol_shooters(self):
        self.pistol_shooters.clear()
        pistol_shooters = DBGetter.get_shooters_at_competition(self.competition_id, 0)
        for shooter in pistol_shooters:
            self.pistol_shooters.append(
                {
                    "Strijelac": f"{shooter['Ime']} {shooter['Prezime']}",
                    "id": shooter['id']
                }
            )
        self.add_shooters(0, self.pistol_shooters)

    def refresh_rifle_shooters(self):
        self.rifle_shooters.clear()
        rifle_shooters = DBGetter.get_shooters_at_competition(self.competition_id, 1)
        for shooter in rifle_shooters:
            self.rifle_shooters.append(
                {
                    "Strijelac": f"{shooter['Ime']} {shooter['Prezime']}",
                    "id": shooter['id']
                }
            )
        self.add_shooters(1, self.rifle_shooters)

    def refresh_shooters(self):
        self.refresh_pistol_shooters()
        self.refresh_rifle_shooters()

    def keep_aspect_ratio(self):
        text_height = tkFont.Font(font=self.font).metrics("linespace")
        y = text_height * (self.max_shooters + 5 + self.additional_weight)
        self.configure(height=y)


class CompetitionsProgramColorPickerToplevel(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.save_and_exit)
        self.grab_set()

        self.geometry("{}x{}".format(800, 450))
        self.font = tkFont.Font(size=14)

        self.frame_button_settings = tk.Frame(self, height=35)
        self.frame_button_settings.columnconfigure(0, weight=1, uniform="cols")
        self.frame_button_settings.columnconfigure(1, weight=3, uniform="cols")
        self.frame_button_settings.rowconfigure(0, weight=1)

        self.lbl_button_font = tk.Label(
            self.frame_button_settings,
            text="Gumbi: ",
            font=self.font
        )
        self.frame_buttons_font = Fonts.FontSettings(
            parent=self.frame_button_settings,
            font_config=Fonts.fonts2["Competitions"]["input"],
            notif_func=lambda: KeepAspectRatio.call_subscribers("Competitions")
        )
        self.lbl_button_font.grid(row=0, column=0, sticky="nse")
        self.frame_buttons_font.grid(row=0, column=1, sticky="nsew")

        self.frame_preview_settings = tk.Frame(self, height=35)
        self.frame_preview_settings.columnconfigure(0, weight=1, uniform="cols")
        self.frame_preview_settings.columnconfigure(1, weight=3, uniform="cols")
        self.frame_preview_settings.rowconfigure(0, weight=1)

        self.lbl_preview_font = tk.Label(
            self.frame_preview_settings,
            text="Napredni prikaz: ",
            font=self.font
        )
        self.frame_preview_font = Fonts.FontSettings(
            parent=self.frame_preview_settings,
            font_config=Fonts.fonts2["Competitions"]["preview"]
        )
        self.lbl_preview_font.grid(row=0, column=0, sticky="nse")
        self.frame_preview_font.grid(row=0, column=1, sticky="nsew")

        self.frame_treeview_setting = tk.Frame(self, height=35)
        self.frame_treeview_setting.columnconfigure(0, weight=1, uniform="cols")
        self.frame_treeview_setting.columnconfigure(1, weight=3, uniform="cols")
        self.frame_treeview_setting.rowconfigure(0, weight=1)

        self.lbl_treeview_font = tk.Label(
            self.frame_treeview_setting,
            text="Tablica: ",
            font=self.font
        )
        self.frame_treeview_font = Fonts.FontSettings(
            parent=self.frame_treeview_setting,
            font_config=Fonts.fonts2["Competitions"]["treeview"]
        )
        self.lbl_treeview_font.grid(row=0, column=0, sticky="nse")
        self.frame_treeview_font.grid(row=0, column=1, sticky="nsew")

        # HHS
        self.frame_HSS_settings = tk.Frame(self, height=35)
        self.frame_HSS_settings.columnconfigure(0, weight=1, uniform="cols")
        self.frame_HSS_settings.columnconfigure(1, weight=3, uniform="cols")
        self.frame_HSS_settings.rowconfigure(0, weight=1)

        self.lbl_HSS_font = tk.Label(
            self.frame_HSS_settings,
            text="HSS: ",
            font=self.font
        )
        self.frame_HSS_font = Fonts.FontSettings(
            parent=self.frame_HSS_settings,
            font_config=Fonts.fonts2["Competitions"]["Downloader"]["treeview"]
        )
        self.lbl_HSS_font.grid(row=0, column=0, sticky="nse")
        self.frame_HSS_font.grid(row=0, column=1, sticky="nsew")

        self.frame_button_settings.pack(side="top", expand=True, fill="x")
        self.frame_preview_settings.pack(side="top", expand=True, fill="x")
        self.frame_treeview_setting.pack(side="top", expand=True, fill="x")
        self.frame_HSS_settings.pack(side="top", expand=True, fill="x")

        self.frame_color = CompetitionsProgramColorPicker(self)
        self.frame_color.pack(side="top", expand=True, fill="both")

    def save_and_exit(self):
        self.destroy()


class CompetitionsProgramColorPicker(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.programs = DBGetter.get_programs()

        self.frame_main = ScrollableFrame.Vertical(self)
        self.frame_main.pack(expand=True, fill="both")

        self.program_color_pickers = []

        self.load_programs()

    def load_programs(self):
        for program in self.programs:
            program_color_picker = CompetitionsProgramColorPickerProgramColor(
                self.frame_main.scrollable_frame,
                program_text=program['Naziv'],
                bg_color=CompetitionPreview.get_bg_color(program['Naziv']),
                text_color=CompetitionPreview.get_fg_color(program['Naziv'])
            )
            self.program_color_pickers.append(program_color_picker)
            self.program_color_pickers[-1].pack(expand=True, side="top", fill="both")

    def save_programs(self):
        for program_color_picker in self.program_color_pickers:
            CompetitionPreview.save_bg_color(
                program_name=program_color_picker.program_name,
                color=program_color_picker.bg_color
            )
            CompetitionPreview.save_fg_color(
                program_name=program_color_picker.program_name,
                color=program_color_picker.text_color
            )


class CompetitionsProgramColorPickerProgramColor(tk.Frame):
    def __init__(self, parent, program_text: str, bg_color: str, text_color: str, height=100, width=100):
        tk.Frame.__init__(self, parent, bg=bg_color, height=height, width=width)

        self.bg_color = bg_color
        self.text_color = text_color
        self.program_name = program_text

        self.font = Fonts.fonts2["CompetitionsPreviewColorPicker"]["font"]

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=4, uniform="rows")
        self.rowconfigure(2, weight=4, uniform="rows")
        self.rowconfigure(3, weight=1, uniform="rows")

        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=5, uniform="cols")
        self.columnconfigure(2, weight=2, uniform="cols")
        self.columnconfigure(3, weight=3, uniform="cols")
        self.columnconfigure(4, weight=1, uniform="cols")

        self.grid_propagate(False)

        self.lbl_program = tk.Label(
            self,
            text=program_text,
            font=self.font,
            bg=bg_color,
            fg=text_color
        )

        self.btn_pick_bg_color = tk.Button(
            self,
            text="Pozadinska boja",
            font=self.font,
            bd=3,
            command=lambda: self._pick_bg_color()
        )

        self.btn_pick_fg_color = tk.Button(
            self,
            text="Boja teksta",
            font=self.font,
            bd=3,
            command=lambda: self._pick_fg_color()
        )

        self.lbl_program.grid(row=1, column=1, rowspan=2, sticky="nsew")

        self.btn_pick_bg_color.grid(row=1, column=3, sticky="nsew")
        self.btn_pick_fg_color.grid(row=2, column=3, sticky="nsew")

    def _pick_bg_color(self):
        color = Tools.color_picker()
        if color:
            self.bg_color = color
            self.configure(bg=color)
            self.lbl_program.configure(bg=color)
            CompetitionPreview.save_bg_color(self.program_name, color)
            Colors.call_subscribers("CompetitionPreview")

    def _pick_fg_color(self):
        color = Tools.color_picker()
        if color:
            self.text_color = color
            self.lbl_program.configure(fg=color)
            CompetitionPreview.save_fg_color(self.program_name, color)
            Colors.call_subscribers("CompetitionPreview")
