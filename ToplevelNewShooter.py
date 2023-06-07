import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import datetime
from CustomWidgets import DateEntry2
from tkinter import messagebox
from dbcommands_rewrite import DBAdder

import sqlTypes


class AddShooter(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        width = 600
        height = 450
        self.geometry("{}x{}".format(width, height))
        self.protocol("WM_DELETE_WINDOW", self.exit_without_saving)
        self.attributes("-topmost", True)

        self.font = tkFont.Font(size=14)

        self.return_values: sqlTypes.ShooterBasicInfo = {
            "Ime": "",
            "Prezime": "",
            "Datum": "",
            "Spol": "",
            "id": 0
        }

        self.cbx_style = ttk.Style()
        self.cbx_style.configure("AddShooterToplevel.TCombobox", font=("Arial", 14))
        self.DateEntry2_style = ttk.Style()
        self.DateEntry2_style.configure("AddShooterToplevel.DateEntry", font=("Arial", 14))

        self.sexes = ["Muško", "Žensko"]

        self.lbl_name = tk.Label(
            self,
            text="Ime:",
            font=self.font
        )

        self.name = tk.StringVar()
        self.ent_name = tk.Entry(
            self,
            width=22,
            textvariable=self.name,
            font=self.font
        )

        self.lbl_lastname = tk.Label(
            self,
            text="Prezime:",
            font=self.font
        )

        self.lastname = tk.StringVar()
        self.ent_lastname = tk.Entry(
            self,
            width=22,
            textvariable=self.lastname,
            font=self.font
        )

        self.lbl_birth_date = tk.Label(
            self,
            text="Datum rođenja:",
            font=self.font
        )

        self.calendar_birth_date = DateEntry2(
            self,
            style="AddShooterToplevel.DateEntry",
            selectmode="day",
            locale="hr_HR",
            font=self.font,
            state="readonly"
        )

        self.lbl_sex = tk.Label(
            self,
            text="Spol:",
            font=self.font
        )

        self.cbx_sex = ttk.Combobox(
            self,
            values=self.sexes,
            style="AddShooterToplevel.TCombobox",
            width=7,
            font=self.font,
            state="readonly"
        )
        self.cbx_sex.current(0)

        self.btn_confirm = tk.Button(
            self,
            text="Dodaj",
            font=self.font,
            bg="lime",
            fg="black",
            command=lambda: self.save_and_exit()
        )

        self.lbl_name.place(relx=0.25, rely=0.1, anchor="center")
        self.ent_name.place(relx=0.6, rely=0.1, anchor="center")

        self.lbl_lastname.place(relx=0.25, rely=0.3, anchor="center")
        self.ent_lastname.place(relx=0.6, rely=0.3, anchor="center")

        self.lbl_birth_date.place(relx=0.35, rely=0.5, anchor="e")
        self.calendar_birth_date.place(relx=0.6, rely=0.5, anchor="center")

        self.lbl_sex.place(relx=0.3, rely=0.7, anchor="e")
        self.cbx_sex.place(relx=0.6, rely=0.7, anchor="center")

        self.btn_confirm.place(relx=0.75, rely=1, anchor="s")

    def exit_without_saving(self):
        self.return_values = None
        self.destroy()

    def save_and_exit(self):
        if self.check_values():
            DBAdder.add_shooter(
                name=self.name.get(),
                lastname=self.lastname.get(),
                sex=self.cbx_sex.get(),
                date_of_birth=str(self.calendar_birth_date.get_date())
            )
            self.destroy()

    def check_name(self) -> bool:
        if self.name.get():
            return True
        return False

    def check_lastname(self) -> bool:
        if self.lastname.get():
            return True
        return False

    def check_date_entry(self) -> bool:
        try:
            datetime.datetime.strptime(str(self.calendar_birth_date.get_date()), "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def check_sex(self) -> bool:
        if self.cbx_sex.get() in self.sexes:
            return True
        return False

    def check_values(self) -> bool:
        if not self.check_name():
            messagebox.askokcancel("Greška", "Ime nije unešeno!")
            return False
        if not self.check_lastname():
            messagebox.askokcancel("Greška", "Prezime nije unešeno!")
            return False
        if not self.check_date_entry():
            messagebox.askokcancel("Greška", "Datum rođenje nije ispravno unešen, ispravan format je (dd. mm. YYYY.)")
            return False
        if not self.check_sex():
            messagebox.askokcancel("Greška", "Spol nije ispravno unešen, koristite padajući izbornik za odabir!")
            return False
        return True
