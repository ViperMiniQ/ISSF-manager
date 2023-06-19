from dbcommands_rewrite import DBGetter, DBUpdate, DBRemover
import ApplicationProperties
import os
from tkinter import messagebox
from ResultExporter import FileTitle
import Downloader
from tkinter import filedialog
import shutil

bilten_path = "/Data/Bilteni/"
startne_liste_path = "/Data/Startne liste/"
pozivno_pismo_path = "/Data/Pozivno pismo/"


def set_hss_id(parent, competition_id: int):
    window = FileTitle(parent, "hss_id")
    window.focus()
    window.wait_window()
    if window.value:
        if DBUpdate.set_competition_hss_id(competition_id, int(window.value)):
            return int(window.value)
    return 0


def remove_bilten(competition_id: int):
    file = DBGetter.get_bilten(competition_id)
    if file:
        ask = messagebox.askyesno(title="Bilten", message="Jeste li sigurni da želite ukloniti bilten?")
        if not ask:
            return
        try:
            os.remove(ApplicationProperties.LOCATION + file)
        except (OSError, FileNotFoundError):
            messagebox.showerror(
                title="Bilten",
                message="Greška uklanjanja datoteke."
            )
            return
        DBRemover.delete_competition_bilten_path(competition_id)
        messagebox.showinfo(
            title="Bilten",
            message="Datoteka je uspješno uklonjena."
        )
        return
    messagebox.showerror(
        title="Bilten",
        message="Datoteka ne postoji."
    )


def remove_startne_liste(competition_id: int):
    file = DBGetter.get_startne_liste(competition_id)
    if file:
        ask = messagebox.askyesno(title="Startne liste", message="Jeste li sigurni da želite ukloniti startne liste?")
        if not ask:
            return
        try:
            os.remove(ApplicationProperties.LOCATION + file)
        except (OSError, FileNotFoundError):
            messagebox.showerror(
                title="Startne liste",
                message="Greška uklanjanja datoteke."
            )
            return
        DBRemover.delete_competition_startne_liste_path(competition_id)
        messagebox.showinfo(
            title="Startne liste",
            message="Datoteka je uspješno uklonjena"
        )
        return
    messagebox.showerror(
        title="Startne liste",
        message="Datoteka ne postoji."
    )


def remove_pozivno_pismo(competition_id: int):
    if ApplicationProperties.PLATFORM == "WINDOWS":
        file = DBGetter.get_pozivno_pismo(competition_id)
        if file:
            ask = messagebox.askyesno(title="Pozivno pismo", message="Jeste li sigurni da želite pozivno pismo?")
            if not ask:
                return
            try:
                os.remove(ApplicationProperties.LOCATION + file)
            except (OSError, FileNotFoundError):
                messagebox.showerror(
                    title="Startne liste",
                    message="Greška uklanjanja datoteke."
                )
                return
            DBRemover.delete_competition_pozivno_pismo(competition_id)
            messagebox.showinfo(
                title="Pozivno pismo",
                message="Datoteka je uspješno uklonjena"
            )
            return
        messagebox.showerror(
            title="Pozivno pismo",
            message="Datoteka ne postoji."
        )


def show_bilten(competition_id: int):
    if ApplicationProperties.PLATFORM == "WINDOWS":
        file = DBGetter.get_bilten(competition_id)
        if file:
            os.startfile(ApplicationProperties.LOCATION + file)
            return
        messagebox.showinfo(
            title="Bilten",
            message="Datoteka nije dodana."
        )


def show_startne_liste(competition_id: int):
    if ApplicationProperties.PLATFORM == "WINDOWS":
        file = DBGetter.get_startne_liste(competition_id)
        if file:
            os.startfile(ApplicationProperties.LOCATION + file)
            return
        messagebox.showinfo(
            title="Startne liste",
            message="Datoteka nije dodana."
        )


def show_pozivno_pismo(competition_id: int):
    if ApplicationProperties.PLATFORM == "WINDOWS":
        file = DBGetter.get_pozivno_pismo(competition_id)
        if file:
            os.startfile(ApplicationProperties.LOCATION + file)
            return
        messagebox.showinfo(
            title="Pozivno pismo",
            message="Datoteka nije dodana."
        )


def experimental_download_bilten(competition_id: int):
    value = DBGetter.get_competition_hss_id(competition_id)
    if value:
        try:
            filename = str(competition_id) + "_bilten"
            extension = Downloader.download_and_save_competition_documents(
                competition_id=value,
                filename=filename,
                path=ApplicationProperties.LOCATION + bilten_path,
                document="Bilten"
            )
            if extension:
                DBUpdate.update_competition_bilten(competition_id, bilten_path + filename + "." + extension)
                messagebox.showinfo(title="Bilten", message="Datoteka je uspješno preuzeta.")
                return True
            messagebox.showerror(
                title="Bilten",
                message="Datoteka nije pronađena."
            )
            return False
        except:
            messagebox.showerror(title="Greška", message="Greška u preuzimanju biltena.")
            return False
    messagebox.showerror(
        title="Greška",
        message="Nije postavljen hss_id natjecanja."
    )
    return False


def experimental_download_startne_liste(competition_id: int):
    value = DBGetter.get_competition_hss_id(competition_id)
    if value:
        try:
            filename = str(competition_id) + "_startne_liste"
            extension = Downloader.download_and_save_competition_documents(
                competition_id=value,
                filename=filename,
                path=ApplicationProperties.LOCATION + startne_liste_path,
                document="Startne liste"
            )
            if extension:
                DBUpdate.update_competition_startne_liste(competition_id,
                                                          startne_liste_path + filename + "." + extension
                )
            messagebox.showinfo(title="Startne liste", message="Datoteka je uspješno preuzeta.")
            return True
        except:
            messagebox.showerror(title="Greška", message="Greška u preuzimanju biltena.")
            return False
    return False


def add_bilten(parent, competition_id: int):
    filename = filedialog.askopenfilename(parent=parent, title="Izaberite datoteku biltena")
    if filename:
        try:
            filename_save_as = str(competition_id) + "_bilten." + filename.split('.')[-1]
            shutil.copy(filename, ApplicationProperties.LOCATION + bilten_path + filename_save_as)
        except:
            messagebox.showerror(title="Bilten",
                                 message="Greška dodavanja datoteke, pokušajte pokrenuti program kao administrator.")
            return False
        DBUpdate.update_competition_bilten(competition_id, bilten_path + filename_save_as)
        messagebox.showinfo(title="Bilten", message="Datoteka uspješno dodana.")
        return True
    return False


def add_startne_liste(parent, competition_id: int):
    filename = filedialog.askopenfilename(parent=parent, title="Izaberite datoteku startne liste")
    if filename:
        try:
            filename_save_as = str(competition_id) + "_startne_liste." + filename.split('.')[-1]
            shutil.copy(filename, ApplicationProperties.LOCATION + startne_liste_path + filename_save_as)
        except:
            messagebox.showerror(title="Startne liste",
                                 message="Greška dodavanja datoteke, pokušajte pokrenuti program kao administrator.")
            return False
        DBUpdate.update_competition_startne_liste(competition_id, startne_liste_path + filename_save_as)
        messagebox.showinfo(title="Startne liste", message="Datoteka je uspješno dodana.")
        return True
    return False


def add_pozivno_pismo(parent, competition_id: int):
    filename = filedialog.askopenfilename(parent=parent, title="Izaberite datoteku pozivnog pisma")
    if filename:
        try:
            filename_save_as = str(competition_id) + "_pozivno_pismo." + filename.split('.')[-1]
            shutil.copy(filename, ApplicationProperties.LOCATION + pozivno_pismo_path + filename_save_as)
        except:
            messagebox.showerror(title="Pozivno pismo",
                                 message="Greška dodavanja datoteke, pokušajte pokrenuti program kao administrator.")
            return False
        DBUpdate.update_competition_pozivno_pismo(competition_id, pozivno_pismo_path + filename_save_as)
        messagebox.showinfo(title="Pozivno pismo", message="Datoteka uspješno dodana.")
        return True
    return False


def experimental_download_pozivno_pismo(competition_id: int):
    value = DBGetter.get_competition_hss_id(competition_id)
    if value:
        try:
            filename = str(competition_id) + "_pozivno_pismo"
            extension = Downloader.download_and_save_competition_documents(
                competition_id=value,
                filename=filename,
                path=ApplicationProperties.LOCATION + pozivno_pismo_path,
                document="Pozivno pismo"
            )
            if extension:
                DBUpdate.update_competition_pozivno_pismo(competition_id,
                                                          pozivno_pismo_path + filename + "." + extension)
            messagebox.showinfo(title="Pozivno pismo", message="Datoteka je uspješno preuzeta.")
            return True
        except:
            messagebox.showerror(title="Greška", message="Greška u preuzimanju biltena.")
            return False