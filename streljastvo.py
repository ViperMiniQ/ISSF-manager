# -*- coding: UTF-8 -*-
import shutil
import tkinter.ttk as ttk
import ApplicationProperties
import CSVExporter
import CustomWidgets
import ItemCreator
import JSONManager
import Changes
import tkinter as tk
import tkinter.font as tkFont
import time
from datetime import datetime
from tkinter import messagebox
import matplotlib
import logging
import sys
import traceback
import HoverInfo
import ResultExporter
import DirectoryHelper
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from PIL import Image, ImageTk
import babel.numbers #needed for pyinstaller, there's a workaround, but keep it anyway
import calendar

import ItemCreator
import locale

import ManageShootersMain
import Results
import StartPage
import ManageArms
import Competitions
import Splash
import Settings
import Plot
import Logger
import KeepAspectRatio
import Fonts
import ctypes
import Colors
from ClubInfo import ClubInfo
from HTMLResults import HTMLResultsToplevel
from dbcommands_rewrite import DBConnector, DBSetter, DBGetter, DBMisc

if ApplicationProperties.PLATFORM == "WINDOWS":
    try:
       ctypes.windll.shcore.SetProcessDpiAwareness(2)  # if windows version >= 8.1
    except Exception:
       ctypes.windll.user32.SetProcessDPIAware()


class GUI(tk.Tk):
    @Logger.benchmark
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        try:
            locale.setlocale(locale.LC_ALL, ApplicationProperties.LC_TIME)
        except (locale.Error, TypeError, ValueError):
            pass

        DirectoryHelper.set_all()

        DBConnector.set_db_filepath(ApplicationProperties.LOCATION + "/Data/strijelci.db")
        DBSetter.prepare_db()

        self.withdraw()

        self.splash_json_file = ApplicationProperties.SPLASH_FILEPATH

        icon_path = ApplicationProperties.LOCATION + "/Data/Ikona/ikona.png"
        icon_splash_path = ApplicationProperties.LOCATION + "/Data/Ikona/ikona.png"

        self.TButton_style = ttk.Style()
        self.TButton_style.configure("TButton")
        self.TButton_style.map("TButton", background=[('active', '!disabled', 'green')])

        self.update_idletasks()
        
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        if ApplicationProperties.SPLASH_FILEPATH:
            splash_width = ApplicationProperties.SPLASH_GEOMETRY["width"]
            splash_height = ApplicationProperties.SPLASH_GEOMETRY["height"]
            splash_at_x = int((screen_width - splash_width) / 2)
            splash_at_y = int((screen_height - splash_height) / 2)
            splash_screen = Splash.Splash(self, icon_splash_path, splash_width, splash_height, splash_at_x, splash_at_y)

        icon = tk.PhotoImage(file=icon_path)
        self.title('GSD 1887 "LOKOMOTIVA" VINKOVCI')
        self.iconphoto(True, icon)
        self.width = 800
        self.height = 450
        self.width_min = 800
        self.height_min = 450
        self.aspect_ratio = 16/9
        self.currently_raised_frame = None
        self.currently_raised_frame_name = None
        self.time_since_resize = time.time()

        self.minsize(self.width_min, self.height_min)

        self.db_file_in_cwd = ApplicationProperties.LOCATION + "/Data/strijelci.db"  # place in separate function
        self.db_file_in_cwd_settings = ApplicationProperties.LOCATION + "/Data/postavke.db"

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.r_font = tkFont.Font(family="Serif", size=10)  #entry rounds font
   
        self.menu = tk.Menu(self, font=tkFont.Font(size=20))
        self.config(menu=self.menu)

        menu_file = tk.Menu(self.menu, tearoff=0)
        menu_club = tk.Menu(self.menu, tearoff=0)
        menu_equipment = tk.Menu(self.menu, tearoff=0)
        self.menu_help = tk.Menu(self.menu, tearoff=0)
        menu_file.add_command(label="Uvezi tablicu")
        menu_file_export = tk.Menu(menu_file, tearoff=0)
        menu_file_export.add_command(label="Izvezi dnevnik kao .xlsx", command=lambda: self.ExportToExcel("dnevnik"))
        menu_file.add_cascade(label='Izvezi tablicu', menu=menu_file_export, underline=0)
        menu_file.add_command(label="Izlaz", command=close_program)
        self.menu.add_cascade(label="Datoteka", menu=menu_file)
        menu_club.add_command(label="Obavijesti F1", command=lambda: self.ShowClass("Start"))
        menu_club.add_separator()
        menu_club.add_command(label="Strijelci F2", command=lambda: self.ShowClass("ManageShooters"))
        menu_club.add_separator()
        menu_club.add_command(label="Natjecanja F4", command=lambda: self.ShowClass("Competitions"))
        menu_club.add_separator()
        menu_club.add_command(label="Statistika F5", command=lambda: self.ShowClass("PlotResults2"))
        menu_club.add_command(label="Dnevnik F6", command=lambda: self.ShowClass("Results"))
        self.menu.add_cascade(label="Rad kluba", menu=menu_club)
        self.menu_help.add_command(label="Pomoć F10", command=lambda: self.activate_help())
        self.menu_help.add_command(label="Verzija F11", command=lambda: VersionInfo(self))
        self.menu_help.add_command(label="Postavke F12", command=lambda: self.ShowClass("Settings"))
        menu_equipment.add_command(label="Oružje CTRL-1", command=lambda: self.ShowClass("ManageArms"))
        menu_equipment.add_separator()
        menu_equipment.add_command(label="Zračni cilindri CTRL-2", command=lambda: ManageArms.AirCylindersToplevel(self))

        self.menu.add_cascade(label="Oprema", menu=menu_equipment)
        self.menu.add_cascade(label="Pomoć", menu=self.menu_help)

        Fonts.refresh_available_fonts()
        try:
            Fonts.load_fonts2(fullscreen_size=self.winfo_vrootwidth())
        except Exception:
            shutil.copy(ApplicationProperties.LOCATION + "/Config/backup/Fonts2.json", ApplicationProperties.LOCATION + "/Config/Fonts2.json")
            Fonts.load_fonts2(fullscreen_size=self.winfo_vrootwidth())
        try:
            Colors.load_colors()
        except Exception:
            shutil.copy(ApplicationProperties.LOCATION + "/Config/backup/Colors.json", ApplicationProperties.LOCATION + "/Config/Colors.json")
            Colors.load_colors()

        self.font_manipulator = Fonts.FontAdjuster()

        if ApplicationProperties.RESPECT_FONTS_DIVISOR:
            KeepAspectRatio.subscribe(self.font_manipulator)

        self.load_pages()

        self.container.bind("<Configure>", self.KeepAspectRatio)

        self.state("zoomed")
        self.ShowClass("Start")

        self.last_configure_time = time.time()
        self.keep_aspect_ratio_is_done = True
        self.after_ids = []

        self.KeepAspectRatio(event=None)
        self.deiconify()

        self.after(10, splash_screen.destroy())

        self.bind("<F1>", lambda event, class_name="Start": self.ShowClass(class_name))
        self.bind("<F2>", lambda event, class_name="ManageShooters": self.ShowClass(class_name))
        self.bind("<F4>", lambda event, class_name="Competitions": self.ShowClass(class_name))
        self.bind("<F5>", lambda event, class_name="PlotResults2": self.ShowClass(class_name))
        self.bind("<F6>", lambda event, class_name="Results": self.ShowClass(class_name))
        self.bind("<F10>", lambda event: self.activate_help())
        self.bind("<F12>", lambda event, class_name="Settings": self.ShowClass(class_name))

        self.bind("<Control-Key-1>", lambda event, class_name="ManageArms": self.ShowClass(class_name))
        self.bind("<Control-Key-2>", lambda event: ManageArms.AirCylindersToplevel(self))

        self.bind("<Control-Key-+>", lambda event: ItemCreator.ShowAll(self))
        self.bind("<Control-Key-0>", lambda event: Fonts.AllFontConfiguratorToplevel(self).wait_window())

        self.bind("<Control-Key-r>", lambda event: self.export_oruzje_to_csv())
        self.bind("<Control-Key-d>", lambda event: self.export_dnevnik_to_csv())
        self.bind("<Control-Key-h>", lambda event: HTMLResultsToplevel(self))

    @staticmethod
    def export_dnevnik_to_csv():
        results = DBGetter.get_results()
        CSVExporter.write_dict_to_csv(ApplicationProperties.LOCATION + "/dnevnik.csv", results)

    @staticmethod
    def export_oruzje_to_csv():
        weapons = DBMisc.weapons_table_with_headers()
        CSVExporter.write_to_csv(ApplicationProperties.LOCATION + "/oruzje.csv", weapons['headers'], weapons['data'])

    def set_geometry(self, x, y):
        self.state("normal")
        self.geometry("{}x{}".format(x, y))

    def load_pages(self):
        for page in (
                Results.Results,
                ManageShootersMain.ManageShooters,
                StartPage.Start,
                Settings.Settings,
                Plot.PlotResults2,
                Competitions.Competitions,
                ManageArms.ManageArms,
                ClubInfo
        ):
            name = page.__name__
            frame = page(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def activate_help(self):
        self.menu_help.entryconfigure(0, label="Pomoć F10" + u"\u2714", command=lambda: self.deactivate_help())
        HoverInfo.activate_all_tooltips()

    def deactivate_help(self):
        self.menu_help.entryconfigure(0, label="Pomoć F10", command=lambda: self.activate_help())
        HoverInfo.deactivate_all_tooltips()

    def IgnoreEvent(self, event):
        return

    def ShowResults(self, competition_id):  # shows the competition results in Results
        results = DBGetter.get_results(
            competition_ids=[competition_id]
        )
        self.frames["Results"].ClearTree()
        if results:
            self.frames["Results"].FilterTree(results)
        self.ShowClass("Results")

    def ExportToExcel(self, table):
        if table == "dnevnik":
            exporter = ResultExporter.ResultExporter(self)
            exporter.focus()
            exporter.update()
            exporter.focus()
            exporter.wait_window()

    def UpdateFromdb(self, modified_table = None):
        if Changes.get_shooters_update():
            Changes.call_refresh_shooters()
            Changes.set_shooters(False)
        if Changes.get_programs_update():
            Changes.call_refresh_programs()
            Changes.set_programs(False)
        if Changes.get_disciplines_update():
            Changes.call_refresh_disciplines()
            Changes.set_disciplines(False)
        if Changes.get_targets_update():
            Changes.call_refresh_targets()
            Changes.set_targets(False)
        if Changes.get_competitions_update():
            Changes.call_refresh_competitions()
            Changes.set_competitions(False)
        if Changes._reminders:
            Changes.call_refresh_reminders()

    def ShowClass(self, name):
        self.UpdateFromdb()
        frame = self.frames[name]
        frame.tkraise()
        self.currently_raised_frame = frame
        self.currently_raised_frame_name = name
        try:
            self.currently_raised_frame.in_focus()
        except Exception:
            pass
    
    def disable_menu(self):
        self.menu.entryconfig("Datoteka", state="disabled")
        self.menu.entryconfig("Rad kluba", state="disabled")
        self.menu.entryconfig("Pomoć", state="disabled")

    def enable_menu(self):
        self.menu.entryconfig("Datoteka", state="normal")
        self.menu.entryconfig("Rad kluba", state="normal")
        self.menu.entryconfig("Pomoć", state="normal")

    def clear_pending_aspect_ratio_after_ids_keep_one(self):
        for i in range(len(self.after_ids) - 1, 0, -1):
            self.after_cancel(self.after_ids.pop(i))

    def KeepAspectRatio(self, event):     
        # self.container.bind("<Configure>", self.IgnoreEvent)
        if time.time() - self.last_configure_time > 2:
            x = self.winfo_width()
            y = self.winfo_height()

            if self.width != x:
                y = int(x/self.aspect_ratio)
                self.width = x
                self.height = y
            elif self.height != y:
                x = int(y * self.aspect_ratio)
                self.width = x
                self.height = y
            else:
                return
            self.configure(cursor="watch")
            self.geometry("{}x{}".format(x, y))
            KeepAspectRatio.x = x
            KeepAspectRatio.y = y
            KeepAspectRatio.call_subscribers()
            self.configure(cursor="")
            self.clear_pending_aspect_ratio_after_ids_keep_one()
            self.last_configure_time = time.time()

            return
            
        self.after_ids.append(self.after(2022, lambda: self.KeepAspectRatio(None)))


class VersionInfo(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.master = parent
        self.width = 450
        self.height = 200

        self.grab_set()

        self.title("Informacije")
        self.geometry("{}x{}".format(self.width, self.height))
        
        self.maxsize(self.width, self.height)
        self.minsize(self.width, self.height)

        info = """
            GSD 1887 "LOKOMOTIVA" VINKOVCI






(c) Dominik Cindrić                dominik.cindric@gsd-lokomotiva-vk.hr
                                                                    
                                                                    """

        self.font = tkFont.Font(family="Serif", size=10)

        self.msg_info = tk.Message(
            self,
            text=info
        )

        self.msg_info.pack(side="top", expand=True, fill="both")


def close_program():
    answer = messagebox.askyesnocancel("Izlaz", "Jeste li sigurni da želite izaći iz programa?")
    try:
        Fonts.save_fonts2_config()
    except Exception:
        pass
    try:
        Colors.save_colors()
    except Exception:
        pass
    if answer:
        program.destroy()


def log_exceptions(type, value, tb):
    logging.info("\n")
    logging.info(time.asctime(time.localtime(time.time())))
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        logging.exception(line)
    logging.exception(value)

    sys.__excepthook__(type, value, tb)  # calls default excepthook


sys.excepthook = log_exceptions


if __name__ == "__main__":
    logging.basicConfig(filename=ApplicationProperties.LOCATION + '/debugging.log', filemode='a', level=logging.INFO)
    logging.info(f"\n\n\nSTART: {datetime.now().strftime('%d. %m. %Y. %H:%M:%S')}\n")
    program = GUI()
    program.report_callback_exception=log_exceptions
    program.protocol("WM_DELETE_WINDOW", close_program)
    program.minsize(800, 450)
    program.mainloop()
