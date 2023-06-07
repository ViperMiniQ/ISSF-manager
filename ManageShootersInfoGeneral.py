import tkinter as tk
import Fonts
import sqlTypes


class ShooterInfoBasic(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.font = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]

        self.lbl_qualifications = tk.Label(
            self,
            font=self.font,
            text="Stručna sprema:"
        )

        self.qualifications = tk.StringVar()
        self.ent_qualifications = tk.Entry(
            self,
            textvariable=self.qualifications,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_job = tk.Label(
            self,
            font=self.font,
            text="Zaposlenje:"
        )

        self.job = tk.StringVar()
        self.ent_job = tk.Entry(
            self,
            textvariable=self.job,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_hobby = tk.Label(
            self,
            font=self.font,
            text="Hobi:"
        )

        self.hobby = tk.StringVar()
        self.ent_hobby = tk.Entry(
            self,
            textvariable=self.hobby,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_bank = tk.Label(
            self,
            font=self.font,
            text="Naziv banke:"
        )

        self.bank = tk.StringVar()
        self.ent_bank = tk.Entry(
            self,
            textvariable=self.bank,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_bank_account = tk.Label(
            self,
            font=self.font,
            text="Žiro račun:"
        )

        self.bank_account = tk.StringVar()
        self.ent_bank_account = tk.Entry(
            self,
            textvariable=self.bank_account,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_qualifications.place(relx=0.1, rely=0.1, anchor="nw")
        self.ent_qualifications.place(relx=0.1, rely=0.14, anchor="nw")

        self.lbl_job.place(relx=0.1, rely=0.22, anchor="nw")
        self.ent_job.place(relx=0.1, rely=0.26, anchor="nw")

        self.lbl_hobby.place(relx=0.1, rely=0.34, anchor="nw")
        self.ent_hobby.place(relx=0.1, rely=0.38, anchor="nw")

        self.lbl_bank.place(relx=0.1, rely=0.46, anchor="nw")
        self.ent_bank.place(relx=0.1, rely=0.5, anchor="nw")

        self.lbl_bank_account.place(relx=0.1, rely=0.58, anchor="nw")
        self.ent_bank_account.place(relx=0.1, rely=0.62, anchor="nw")

    def UpdateValues(self, shooter_general_info: sqlTypes.ShooterGeneralInfo):
        self.qualifications.set(shooter_general_info['StrucnaSprema'])
        self.job.set(shooter_general_info['Zaposlenje'])
        self.hobby.set(shooter_general_info['Hobi'])
        self.bank.set(shooter_general_info['Banka'])
        self.bank_account.set(shooter_general_info['Ziro'])

    def get_values(self) -> sqlTypes.ShooterGeneralInfo:
        shooter_general_info: sqlTypes.ShooterGeneralInfo = {
            "id": 0,
            "StrucnaSprema": self.qualifications.get(),
            "Zaposlenje": self.job.get(),
            "Hobi": self.hobby.get(),
            "Banka": self.bank.get(),
            "Ziro": self.bank_account.get()
        }
        return shooter_general_info
