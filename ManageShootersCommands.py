import shutil
import tkinter as tk
from tkinter import filedialog
import ManageShootersMain
import tkinter.font as tkFont
from datetime import datetime
import ApplicationProperties
import Changes
import CheckbuttonFrame
import Colors
import Fonts
import os
from tkinter import messagebox
from CustomWidgets import DateEntry2
import Notification
import ResultsTree
from tkPDFViewer import tkPDFViewer
import pathlib
import Tools
from dbcommands_rewrite import DBAdder, DBGetter, DBUpdate, DBRemover


class ShooterCommands(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.font = Fonts.fonts2["ManageShooters"]["Commands"]["buttons"]["font"]
        self.font_title = Fonts.fonts2["ManageShooters"]["Commands"]["title"]["font"]
        self.controller = parent
        self.shooter_title = tk.StringVar()
        self.registration = tk.IntVar()
        self.grid_propagate(False)

        # <GRID> #
        for y in range(0, 10, 1):
            self.rowconfigure(y, weight=1, uniform="shooter_rows")

        for x in range(0, 10, 1):
            self.columnconfigure(x, weight=1, uniform="shooter_columns")
        # </GRID> #

        self.lbl_shooter_title = tk.Label(
            self,
            font=self.font_title,
            textvariable=self.shooter_title,
            text="Nije izabran strijelac",
            fg="black",
        )

        self.lbl_doctor_expire = tk.Label(
            self,
            text="Liječnički vrijedi do:",
            font=self,
        )

        self.lbl_registration = tk.Label(
            self,
            text="Registracija:",
            font=self,
        )

        self.btn_arms = tk.Button(
            self,
            text="Oružje",
            bg="red3",
            font=self.font
        )

        self.btn_add_reminder = tk.Button(
            self,
            bg="blue",
            fg="black",
            text="Dodaj podsjetnik",
            font=self.font,
            command=lambda: self.add_reminder()
        )

        self.btn_doctors_pdf = tk.Button(
            self,
            text="Liječnički PDF",
            font=self.font,
            command=self.show_doctors_pdf
        )

        self.btn_seasons = tk.Button(
            self,
            text="Registracije",
            font=self.font,
            command=self.show_seasons
        )

        self.btn_notification_config = tk.Button(
            self,
            text="Konfiguracija obavijesti",
            font=self.font,
            bg="deep sky blue",
            fg="black",
            command=self.show_notification_config
        )

        self.lbl_shooter_title.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.btn_notification_config.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.btn_doctors_pdf.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.btn_seasons.grid(row=8, column=0, columnspan=2, sticky="nsew")

        self.btn_add_reminder.grid(row=8, column=3, columnspan=2, sticky="nsew")

    def add_reminder(self):
        notification = Notification.AddNotification(self, title=self.lbl_shooter_title.cget("text"))
        notification.grab_set()
        notification.focus()
        notification.wait_window()

    def show_notification_config(self):
        window = ConfigureShooterNotifications(self, ManageShootersMain.ManageShooters.current_shooter_id)
        window.focus()
        window.wait_window()
        Changes.set_reminders()

    def show_seasons(self):
        window = ShooterSeasonsToplevel(self, shooter_id=self.controller.current_shooter_id)
        window.focus()
        window.wait_window()
        self.refresh_btn_colors()

    def show_doctors_pdf(self):
        window = PDFDoctors(self, shooter_id=self.controller.current_shooter_id)
        window.focus()
        window.wait_window()
        self.refresh_btn_colors()

    def check_registration(self):
        registrations = DBGetter.get_shooter_registrations(self.controller.current_shooter_id)
        if not registrations:
            self.btn_seasons.configure(bg="gray")
            return False
        registrations = sorted(registrations, key=lambda d: d["Vrijedi do"], reverse=True)
        if datetime.strptime(registrations[0]["Vrijedi do"], "%Y-%m-%d") > datetime.now():
            self.btn_seasons.configure(bg="lime")
            return True
        self.btn_seasons.configure(bg="red")
        return False

    def check_doctor(self):
        doctors = DBGetter.get_shooter_doctors_pdf(self.controller.current_shooter_id)
        if not doctors:
            self.btn_doctors_pdf.configure(bg="gray")
            return
        doctors = sorted(doctors, key=lambda d: d['Vrijedi do'], reverse=True)
        if datetime.strptime(doctors[0]["Vrijedi do"], "%Y-%m-%d") > datetime.now():
            self.btn_doctors_pdf.configure(bg="lime")
            return
        self.btn_doctors_pdf.configure(bg="red")

    def refresh_btn_colors(self):
        if self.check_registration():
            self.check_doctor()
            return
        self.btn_doctors_pdf.configure(bg="gray")
        
    def update_values(self, title: str):
        self.set_title(title)
        self.refresh_btn_colors()

    def set_title(self, title: str):
        self.shooter_title.set(title)


# TODO: check if all directories exist before starting program
class DoctorsPDF(tk.Frame):
    def __init__(self, parent, shooter_id: int):
        tk.Frame.__init__(self, parent)

        self.pdf_path_in_app_folder = "/Data/Lijecnicki/"

        self.pdf_path = ApplicationProperties.LOCATION + self.pdf_path_in_app_folder  # "/Data/Lijecnicki/"
        self.shooter_id = shooter_id

        self.font_btn = Fonts.fonts2["ManageShooters"]["DoctorPDFs"]["buttons"]["font"]

        self.tree_columns = {
            "Strijelac": 1,
            "Vrijedi od": 1,
            "Vrijedi do": 1,
            "Path": 0,
            "pdf_id": 0
        }

        self.tree_columns_widths = {
            "Strijelac": 400,
            "Vrijedi od": 200,
            "Vrijedi do": 200,
            "Path": 1,
            "pdf_id": 1
        }

        self.tree_columns_types = {
            "Strijelac": "str",
            "Vrijedi od": "date",
            "Vrijedi do": "date",
            "Path": "str",
            "pdf_id": "int"
        }

        self.frame_tree = ResultsTree.ResultsTree(self, self, self.tree_columns, self.tree_columns_widths,
                                                  self.tree_columns_types, "ManageShootersDoctors",
                                                  Fonts.fonts2["ManageShooters"]["DoctorPDFs"]["treeview"]["font"])
        self.frame_tree.set_colors(
            even_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["bg"],
            odd_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["bg"],
            even_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["fg"],
            odd_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["fg"],
        )
        self.frame_btns = tk.Frame(self)

        self.btn_add = tk.Button(
            self.frame_btns,
            text="Dodaj",
            font=self.font_btn,
            command=self.add_pdf,
            bg="lime",
            fg="black"
        )

        self.btn_delete = tk.Button(
            self.frame_btns,
            font=self.font_btn,
            text=u"\u2421",
            fg="black",
            bg="red",
            command=self.delete_doctors
        )

        self.btn_preview = tk.Button(
            self.frame_btns,
            text="Prikaži",
            font=self.font_btn,
            command=self.preview_entry,
            fg="black",
            bg="yellow"
        )

        self.btn_edit = tk.Button(
            self.frame_btns,
            font=self.font_btn,
            text=u"\u270D",
            bg="green",
            fg="black",
            command=self.edit_pdf
        )

        self.rowconfigure(0, weight=15, uniform="rows")
        self.rowconfigure(1, weight=1, uniform="rows")
        self.columnconfigure(0, weight=1)

        self.frame_btns.rowconfigure(0, weight=1)
        for y in range(0, 7, 1):
            self.frame_btns.columnconfigure(y, weight=1, uniform="frame_btns_cols")

        self.btn_delete.grid(row=0, column=0, sticky="nsew")
        self.btn_edit.grid(row=0, column=2, sticky="nsew")
        self.btn_preview.grid(row=0, column=4, sticky="nsew")
        self.btn_add.grid(row=0, column=6, sticky="nsew")

        self.frame_tree.grid(row=0, column=0, sticky="nsew")
        self.frame_btns.grid(row=1, column=0, sticky="nsew")

        self.refresh()

    def delete_doctors(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        ask = messagebox.askokcancel(
            title="Ukloni liječnički",
            message=f"Jeste li sigurni da želite ukloniti liječničku potvrdu strijelca "
                    f"{values['Strijelac']} \n"
                    f"u trajanju {values['Vrijedi od']} - {values['Vrijedi do']}?"
        )
        if ask:
            DBRemover.remove_doctors_pdf(
                pdf_id=values['pdf_id']
            )
            try:
                pathlib.Path.unlink(ApplicationProperties.LOCATION + values['Path'])
            except FileNotFoundError:
                pass
            finally:
                Changes.set_reminders()
                self.refresh()

    def preview_entry(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        if ApplicationProperties.PLATFORM == "WINDOWS":
            os.startfile(ApplicationProperties.LOCATION + values['Path'])

    def add_pdf(self):
        window = AddDoctorsPDF(self)
        window.focus()
        window.wait_window()
        if window.values['pdf_path']:
            pdf_id = DBAdder.add_doctors_pdf(
                shooter_id=self.shooter_id,
                path="",
                date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                date_to=window.values["date_to"].strftime("%Y-%m-%d"),
                get_id=True
            )
            if pdf_id:
                try:
                    saved_path = self.save_pdf_to_disk(window.values['pdf_path'], pdf_id)
                except Exception:
                    DBRemover.remove_doctors_pdf(pdf_id)
                    return
                DBUpdate.update_shooter_doctors_pdf(
                    path=saved_path,
                    date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                    date_to=window.values["date_to"].strftime("%Y-%m-%d"),
                    shooter_id=self.shooter_id,
                    pdf_id=pdf_id
                )
                Changes.set_reminders()
                self.refresh()
                return

    def edit_pdf(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        window = AddDoctorsPDF(
            self,
            pdf_path=values['Path'],
            date_from=Tools.croatian_date_format_to_SQL(values['Vrijedi od']),
            date_to=Tools.croatian_date_format_to_SQL(values['Vrijedi do'])
        )
        window.focus()
        window.wait_window()
        if window.values:
            try:
                saved_path = self.save_pdf_to_disk(window.values['pdf_path'], values['pdf_id'])
            except Exception:
                return
            DBUpdate.update_shooter_doctors_pdf(
                pdf_id=values["pdf_id"],
                shooter_id=self.shooter_id,
                path=saved_path,
                date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                date_to=window.values["date_to"].strftime("%Y-%m-%d"),
            )
            Changes.set_reminders()
            self.refresh()

    def save_pdf_to_disk(self, path_copy_from: str, pdf_id: int):
        try:
            path_copy_to = self.pdf_path + str(pdf_id) + "_lijecnicki.pdf"
            shutil.copy(path_copy_from, path_copy_to)
            return self.pdf_path_in_app_folder + str(pdf_id) + "_lijecnicki.pdf"
        except (IOError, PermissionError) as e:
            messagebox.showerror(
                title="Greška",
                message="Greška prilikom prijenosa datoteke, pokušajte pokrenuti program kao administrator."
            )
            raise e

    def refresh(self):
        self.frame_tree.ClearTree()
        doctors = DBGetter.get_shooter_doctors_pdf(self.shooter_id)
        for doctor in doctors:
            doctor["Strijelac"] = f"{doctor['Ime']} {doctor['Prezime']}"
            doctor["Vrijedi do"] = Tools.SQL_date_format_to_croatian(doctor["Vrijedi do"])
            doctor["Vrijedi od"] = Tools.SQL_date_format_to_croatian(doctor["Vrijedi od"])
            self.frame_tree.add_values_to_row(doctor, False)
        self.frame_tree.keep_aspect_ratio()

    def set_new_shooter(self, shooter_id: int):
        self.shooter_id = shooter_id
        self.refresh()


class AllDoctorsPDFToplevel(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.geometry("{}x{}".format(800, 600))

        self.frame = AllDoctorsPDFFrame(self)
        self.frame.pack(expand=True, fill="both")

        self.frame.refresh()


class AllDoctorsPDFFrame(DoctorsPDF):
    def __init__(self, parent):
        DoctorsPDF.__init__(self, parent, 0)

        self.btn_add.grid_forget()
        self.btn_delete.grid_forget()
        self.btn_edit.grid_forget()

    def refresh(self):
        shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters() + DBGetter.get_retired_shooters()
        self.frame_tree.ClearTree()
        for shooter in shooters:
            doctors = DBGetter.get_shooter_doctors_pdf(shooter['id'])
            for doctor in doctors:
                doctor["Strijelac"] = f"{doctor['Ime']} {doctor['Prezime']}"
                doctor["Vrijedi do"] = Tools.SQL_date_format_to_croatian(doctor["Vrijedi do"])
                doctor["Vrijedi od"] = Tools.SQL_date_format_to_croatian(doctor["Vrijedi od"])
                self.frame_tree.add_values_to_row(doctor, False)
        self.frame_tree.keep_aspect_ratio()


class AddDoctorsPDFFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.controller = parent
        self.grid_propagate(False)

        self.pdf = tkPDFViewer.ShowPdf()

        self.font_btns = Fonts.fonts2["ManageShooters"]["DoctorPDFs"]["NewDoctorPDF"]["buttons"]["font"]

        self.frame_pdf = tk.Frame(self)
        self.frame_dates = tk.Frame(self)
        self.frame_btns = tk.Frame(self)

        self.pdf_path = ""

        self.btn_choose_pdf = tk.Button(
            self.frame_btns,
            font=self.font_btns,
            text="Odaberi datoteku",
            command=self.btn_choose_pdf_pressed,
            bg="yellow",
            fg="black"
        )

        self.lbl_date_to = tk.Label(
            self.frame_dates,
            font=self.font_btns,
            text="Vrijedi do:"
        )

        self.date_to = DateEntry2(
            self.frame_dates,
            selectmode="day",
            font=self.font_btns,
            locale="hr_HR",
            state="readonly"
        )

        self.lbl_date_from = tk.Label(
            self.frame_dates,
            font=self.font_btns,
            text="Vrijedi od:"
        )

        self.date_from = DateEntry2(
            self.frame_dates,
            font=self.font_btns,
            selectmode="day",
            locale="hr_HR",
            state="readonly"
        )

        self.btn_add = tk.Button(
            self.frame_btns,
            font=self.font_btns,
            text="Dodaj",
            bg="lime",
            fg="black",
            command=self.save_and_exit,
            state="disabled"
        )

        self.frame_dates.rowconfigure(0, weight=1)
        self.frame_dates.columnconfigure(0, weight=1, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(1, weight=3, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(2, weight=3, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(3, weight=2, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(4, weight=3, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(5, weight=3, uniform="frame_dates_cols")
        self.frame_dates.columnconfigure(6, weight=1, uniform="frame_dates_cols")

        self.lbl_date_from.grid(row=0, column=1, sticky="nsew")
        self.date_from.grid(row=0, column=2, sticky="nsew")
        self.lbl_date_to.grid(row=0, column=4, sticky="nsew")
        self.date_to.grid(row=0, column=5, sticky="nsew")

        self.frame_btns.rowconfigure(0, weight=1)
        self.frame_btns.columnconfigure(0, weight=2, uniform="frame_btns_cols")
        self.frame_btns.columnconfigure(1, weight=5, uniform="frame_btns_cols")
        self.frame_btns.columnconfigure(2, weight=1, uniform="frame_btns_cols")

        self.btn_choose_pdf.grid(row=0, column=0, sticky="nsew")
        self.btn_add.grid(row=0, column=2, sticky="nsew")

        self.rowconfigure(0, weight=12, uniform="rows")
        self.rowconfigure(1, weight=1, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=1, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")

        self.columnconfigure(0, weight=1)

        self.frame_pdf.grid(row=0, column=0, sticky="nsew")
        self.frame_dates.grid(row=2, column=0, sticky="nsew")
        self.frame_btns.grid(row=4, column=0, sticky="nsew")

    def btn_choose_pdf_pressed(self):
        if self.add_pdf():
            self.btn_add.configure(state="normal")
            return
        self.btn_add.configure(state="disabled")

    def save_and_exit(self):
        self.controller.save_and_exit()

    def add_pdf(self, filename: str = None):
        if filename is None:
            filename = filedialog.askopenfilename(
                parent=self, title="Izaberite datoteku",
                filetypes=[('PDF', ('.pdf',))]
            )
        if filename:
            for child in self.frame_pdf.winfo_children():
                child.destroy()
            try:
                self.pdf.img_object_li.clear()
                new_view = self.pdf.pdf_view(self.frame_pdf, pdf_location=filename, width=800, height=500)
                new_view.pack(expand=True, fill="both")
                self.pdf_path = filename
                return True
            except Exception:
                return False
        return False


class AddDoctorsPDF(tk.Toplevel):
    def __init__(self, parent, pdf_path: str = "", date_from: str = "", date_to: str = ""):
        tk.Toplevel.__init__(self, parent)

        self.values = {}
        self.grab_set()

        self.geometry("{}x{}+{}+{}".format(800, 450, 0, 0))
        self.pack_propagate(False)

        self.frame_add = AddDoctorsPDFFrame(self)
        self.frame_add.pack(expand=True, fill="both")

        if date_from:
            self.frame_add.date_from.set_date(Tools.SQL_date_format_to_croatian(date_from))
        if date_to:
            self.frame_add.date_to.set_date(Tools.SQL_date_format_to_croatian(date_to))
        if pdf_path != "":
            self.frame_add.add_pdf(ApplicationProperties.LOCATION + pdf_path)
            self.frame_add.update_idletasks()
            self.frame_add.btn_add.configure(state="normal")

    def save_and_exit(self):
        self.values = {
            "date_from": self.frame_add.date_from.get_date(),
            "date_to": self.frame_add.date_to.get_date(),
            "pdf_path": self.frame_add.pdf_path
        }
        self.destroy()


class PDFDoctors(tk.Toplevel):
    def __init__(self, parent, shooter_id: int):
        tk.Toplevel.__init__(self, parent)

        self.title("Liječnički")
        self.grab_set()

        self.geometry("{}x{}".format(800, 600))

        self.pack_propagate(False)

        self.frame_main = DoctorsPDF(self, shooter_id)
        self.frame_main.pack(expand=True, fill="both")
        self.frame_main.refresh()


class ManageShooterSeasonsFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.controller = parent
        self.grid_propagate(False)

        self.lbl_from = tk.Label(
            self,
            text="Vrijedi od:"
        )

        self.date_from = DateEntry2(
            self,
            selectmode="day",
            locale="hr_HR",
            state="readonly"
        )

        self.lbl_to = tk.Label(
            self,
            text="Vrijedi do:"
        )

        self.date_to = DateEntry2(
            self,
            selectmode="day",
            locale="hr_HR",
            state="readonly"
        )

        self.btn_confirm = tk.Button(
            self,
            text="Potvrdi",
            bg="lime",
            fg="black",
            command=self.save_and_exit
        )

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=2, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=2, uniform="rows")

        self.columnconfigure(0, weight=2, uniform="cols")
        self.columnconfigure(1, weight=2, uniform="cols")
        self.columnconfigure(2, weight=1, uniform="cols")
        self.columnconfigure(3, weight=2, uniform="cols")
        self.columnconfigure(4, weight=2, uniform="cols")

        self.lbl_from.grid(row=1, column=0, sticky="nsew")
        self.date_from.grid(row=1, column=1, sticky="nsew")
        self.lbl_to.grid(row=1, column=3, sticky="nsew")
        self.date_to.grid(row=1, column=4, sticky="nsew")

        self.btn_confirm.grid(row=3, column=1, columnspan=3, sticky="nsew")

    def save_and_exit(self):
        self.controller.save_and_exit()


class ManageShooterSeasons(tk.Toplevel):
    def __init__(self, parent, date_from: datetime.date = None, date_to: datetime.date = None, pdf_path: str = ""):
        tk.Toplevel.__init__(self, parent)

        self.values = {}
        self.grab_set()

        self.geometry("{}x{}".format(800, 600))

        self.frame_main = AddDoctorsPDFFrame(self)

        if date_from:
            self.frame_main.date_from.set_date(date_from)
        if date_to:
            self.frame_main.date_to.set_date(date_to)
        if pdf_path != "":
            self.frame_main.add_pdf(ApplicationProperties.LOCATION + pdf_path)
            self.frame_main.update_idletasks()
            self.frame_main.btn_add.configure(state="normal")

        self.frame_main.pack(expand=True, fill="both")

    def save_and_exit(self):
        self.values = {
            "date_from": self.frame_main.date_from.get_date(),
            "date_to": self.frame_main.date_to.get_date(),
            "pdf_path": self.frame_main.pdf_path
        }
        self.destroy()


class ShooterSeasons(tk.Frame):
    def __init__(self, parent, shooter_id):
        tk.Frame.__init__(self, parent)

        self.pdf_path_in_app_folder = "/Data/BIB/"
        self.pdf_path = ApplicationProperties.LOCATION + self.pdf_path_in_app_folder

        self.shooter_id = shooter_id

        self.font_btn = Fonts.fonts2["ManageShooters"]["DoctorPDFs"]["buttons"]["font"]

        self.tree_columns = {
            "Strijelac": 1,
            "Vrijedi od": 1,
            "Vrijedi do": 1,
            "Path": 0,
            "pdf_id": 0
        }

        self.tree_columns_widths = {
            "Strijelac": 400,
            "Vrijedi od": 200,
            "Vrijedi do": 200,
            "Path": 1,
            "pdf_id": 1
        }

        self.tree_columns_types = {
            "Strijelac": "str",
            "Vrijedi od": "date",
            "Vrijedi do": "date",
            "Path": "str",
            "pdf_id": "int"
        }

        self.frame_tree = ResultsTree.ResultsTree(self, self, self.tree_columns, self.tree_columns_widths,
                                                  self.tree_columns_types, "ShooterSeasons",
                                                  Fonts.fonts2["ManageShooters"]["Registrations"]["treeview"]["font"])
        self.frame_tree.set_colors(
            even_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["bg"],
            odd_row_bg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["bg"],
            even_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["even_rows"]["fg"],
            odd_row_fg=Colors.colors["ManageShooters"]["DoctorPDFs"]["treeview"]["odd_rows"]["fg"],
        )
        self.frame_btns = tk.Frame(self)

        self.btn_add = tk.Button(
            self.frame_btns,
            text="Dodaj",
            font=self.font_btn,
            command=self.add_season,
            bg="lime",
            fg="black"
        )

        self.btn_edit = tk.Button(
            self.frame_btns,
            text=u"\u270D",
            font=self.font_btn,
            command=self.edit_season,
            bg="green",
            fg="black"
        )

        self.btn_delete = tk.Button(
            self.frame_btns,
            font=self.font_btn,
            text=u"\u2421",
            fg="black",
            bg="red",
            command=self.delete_season
        )

        self.btn_open_pdf = tk.Button(
            self.frame_btns,
            font=self.font_btn,
            text="Prikaži",
            bg="yellow",
            command=self.open_pdf
        )

        self.frame_btns.rowconfigure(0, weight=1)
        for y in range(0, 7, 1):
            self.frame_btns.columnconfigure(y, weight=1, uniform="frame_btns_cols")

        self.btn_add.grid(row=0, column=6, sticky="nsew")
        self.btn_edit.grid(row=0, column=2, sticky="nsew")
        self.btn_open_pdf.grid(row=0, column=4, sticky="nsew")
        self.btn_delete.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=15, uniform="rows")
        self.rowconfigure(1, weight=1, uniform="rows")

        self.frame_tree.grid(row=0, column=0, sticky="nsew")
        self.frame_btns.grid(row=1, column=0, sticky="nsew")

        self.refresh()

    def open_pdf(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        if ApplicationProperties.PLATFORM == "WINDOWS":
            os.startfile(ApplicationProperties.LOCATION + values['Path'])

    def refresh(self):
        self.frame_tree.ClearTree()
        shooters = DBGetter.get_shooter_registrations(self.shooter_id)
        for shooter in shooters:
            shooter["Strijelac"] = f"{shooter['Ime']} {shooter['Prezime']}"
            shooter["Vrijedi od"] = Tools.SQL_date_format_to_croatian(shooter['Vrijedi od'])
            shooter["Vrijedi do"] = Tools.SQL_date_format_to_croatian(shooter['Vrijedi do'])
            self.frame_tree.add_values_to_row(shooter, False)
        self.frame_tree.keep_aspect_ratio()

    def delete_season(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        ask = messagebox.askyesno(
            title="Obriši registraciju",
            message=f"Jeste li sigurni da želite obrisati registraciju u periodu \n {values['Vrijedi od']} - {values['Vrijedi do']}\n"
                    f"za strijelca {values['Strijelac']}?"
        )
        if ask:
            DBRemover.delete_season(
                pdf_id=values['pdf_id']
            )
            try:
                pathlib.Path.unlink(ApplicationProperties.LOCATION + values['Path'])
            except FileNotFoundError:
                pass
            finally:
                Changes.set_reminders()
                self.refresh()

    def add_season(self):
        window = ManageShooterSeasons(self)
        window.focus()
        window.wait_window()
        if window.values:
            pdf_id = DBAdder.add_shooter_registration(
                shooter_id=self.shooter_id,
                date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                date_to=window.values["date_to"].strftime("%Y-%m-%d"),
                path="",
                get_id=True
            )
            if pdf_id:
                try:
                    saved_path = self.save_pdf_to_disk(window.values['pdf_path'], pdf_id)
                except Exception:
                    DBRemover.delete_season(pdf_id)
                    return
                DBUpdate.update_shooter_registration(
                    pdf_id=pdf_id,
                    path=saved_path,
                    date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                    date_to=window.values["date_to"].strftime("%Y-%m-%d"),
                    shooter_id=self.shooter_id
                )
                Changes.set_reminders()
                self.refresh()

    def edit_season(self):
        values = self.frame_tree.get_values_of_selected_row()
        if not values:
            return
        window = AddDoctorsPDF(
            self,
            date_from=Tools.croatian_date_format_to_SQL(values['Vrijedi od']),
            date_to=Tools.croatian_date_format_to_SQL(values['Vrijedi do']),
            pdf_path=values['Path'],
        )
        window.focus()
        window.wait_window()
        if window.values:
            try:
                saved_path = self.save_pdf_to_disk(window.values['pdf_path'], values['pdf_id'])
            except Exception:
                return
            DBUpdate.update_shooter_registration(
                shooter_id=self.shooter_id,
                date_from=window.values["date_from"].strftime("%Y-%m-%d"),
                date_to=window.values["date_to"].strftime("%Y-%m-%d"),
                path=saved_path,
                pdf_id=values['pdf_id']
            )
            Changes.set_reminders()
            self.refresh()

    def save_pdf_to_disk(self, path_copy_from: str, pdf_id: int):
        try:
            path_copy_to = self.pdf_path + str(pdf_id) + "_bib.pdf"
            shutil.copy(path_copy_from, path_copy_to)
            return self.pdf_path_in_app_folder + str(pdf_id) + "_bib.pdf"
        except (IOError, PermissionError) as e:
            messagebox.showerror(
                title="Greška",
                message="Greška prilikom prijenosa datoteke, pokušajte pokrenuti program kao administrator."
            )
            raise e


class AllShooterSeasonsFrame(ShooterSeasons):
    def __init__(self, parent):
        ShooterSeasons.__init__(self, parent, 0)

        self.btn_add.grid_forget()
        self.btn_delete.grid_forget()
        self.btn_edit.grid_forget()

    def refresh(self):
        shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters() + DBGetter.get_retired_shooters()
        self.frame_tree.ClearTree()
        for shooter in shooters:
            registrations = DBGetter.get_shooter_registrations(shooter['id'])
            for registration in registrations:
                registration["Strijelac"] = f"{registration['Ime']} {registration['Prezime']}"
                registration["Vrijedi do"] = Tools.SQL_date_format_to_croatian(registration["Vrijedi do"])
                registration["Vrijedi od"] = Tools.SQL_date_format_to_croatian(registration["Vrijedi od"])
                self.frame_tree.add_values_to_row(registration, False)
        self.frame_tree.keep_aspect_ratio()


class AllShooterSeasonsToplevel(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.geometry("{}x{}".format(800, 600))

        self.frame = AllShooterSeasonsFrame(self)
        self.frame.pack(expand=True, fill="both")

        self.frame.refresh()


class ShooterSeasonsToplevel(tk.Toplevel):
    def __init__(self, parent, shooter_id: int):
        tk.Toplevel.__init__(self, parent)
        self.grab_set()
        self.title("Registracije")
        self.geometry("{}x{}".format(800, 600))

        self.frame_main = ShooterSeasons(self, shooter_id)
        self.frame_main.pack(expand=True, fill="both")
        self.frame_main.refresh()

# TODO: when adding doctors or BIB, make sure date_to is higher than date_from


class ConfigureShooterNotifications(tk.Toplevel):
    def __init__(self, parent, shooter_id: int):
        tk.Toplevel.__init__(self, parent)

        self.shooter_id = shooter_id

        self.geometry("{}x{}".format(350, 500))

        self.notifications = {
            "Liječnički": DBGetter.get_notification_shooter_doctor(shooter_id),
            "Osobna": DBGetter.get_notification_shooter_NPIN(shooter_id),
            "Putovnica": DBGetter.get_notification_shooter_passport(shooter_id),
            "Rođendan:": DBGetter.get_notification_shooter_birthday(shooter_id)
        }

        self.values = {}

        self.frame_main = CheckbuttonFrame.CheckboxFrame(
            self, width=1, height=1,
            cbx_dict=self.notifications,
            font_size=14,
            color="deep sky blue",
            title="Prikazuj obavijesti za:"
        )

        self.btn_confirm = tk.Button(
            self,
            text="Potvrdi",
            bg="lime",
            fg="black",
            font=tkFont.Font(size=14),
            command=self.save_and_exit
        )

        self.frame_main.pack(side="top", expand=True, fill="both")
        self.btn_confirm.pack(side="bottom", fill="x")

    def save_and_exit(self):
        values = self.frame_main.get_values()
        DBUpdate.update_notification_shooter_doctor(self.shooter_id, values['Liječnički'])
        DBUpdate.update_notification_shooter_NPIN(self.shooter_id, values['Osobna'])
        DBUpdate.update_notification_shooter_passport(self.shooter_id, values['Putovnica'])
        DBUpdate.update_notification_shooter_birthday(self.shooter_id, values['Rođendan'])
        Changes.set_reminders()
        self.destroy()

# TODO: registracije.datum_do needs to be greater or EQUAL to current_date
# TODO: scroll all the way up when resetting reminders
# TODO: tkPDFViewer: change getImageData to tobytes
# TODO: tkPDFViewer: change getPixmap to get_pixmap
