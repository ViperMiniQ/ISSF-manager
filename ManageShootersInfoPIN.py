import tkinter as tk
from datetime import datetime
import Fonts
import sqlTypes
from CustomWidgets import DateEntry2


class ShooterPINInformation(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.font = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]
        self.controller = parent
        self.validate_numbers = (self.register(self.ValidateNumbers))

        self.lbl_NPIN = tk.Label(
            self,
            text="Broj osobne:",
            font=self.font
        )

        self.NPIN = tk.StringVar()
        self.NPIN.set("")
        self.ent_NPIN = tk.Entry(
            self,
            textvariable=self.NPIN,
            font=self.font,
            width=15,
            validatecommand=(self.validate_numbers, "%P"),
            bd=3
        )

        self.lbl_NPIN_expire = tk.Label(
            self,
            text="Osobna vrijedi do:",
            font=self.font
        )

        self.calendar_NPIN_expire = DateEntry2(
            self,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )

        self.NPIN_permament = tk.IntVar()
        self.chk_NPIN_permament = tk.Checkbutton(
            self,
            variable=self.NPIN_permament,
            font=self.font,
            text="Osobna je trajna",
            command=lambda: self.CheckNPINPermanent()
        )

        self.lbl_NPIN_place = tk.Label(
            self,
            font=self.font,
            text="Mjesto izdavanja osobne:"
        )

        self.NPIN_place = tk.StringVar()
        self.ent_NPIN_place = tk.Entry(
            self,
            textvariable=self.NPIN_place,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_passport = tk.Label(
            self,
            font=self.font,
            text="Broj putovnice:"
        )

        self.passport = tk.StringVar()
        self.ent_passport = tk.Entry(
            self,
            font=self.font,
            textvariable=self.passport,
            width=15,
            bd=3
        )

        self.lbl_passport_expire = tk.Label(
            self,
            font=self.font,
            text="Datum isteka putovnice:"
        )

        self.calendar_passport_expire = DateEntry2(
            self,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )

        self.passport_exists = tk.IntVar()
        self.chk_passport_exists = tk.Checkbutton(
            self,
            variable=self.passport_exists,
            text="Nema putovnicu",
            font=self.font,
            command=lambda: self.CheckPassport()
        )

        self.lbl_passport_place = tk.Label(
            self,
            font=self.font,
            text="Mjesto izdavanja putovnice:"
        )

        self.passport_place = tk.StringVar()
        self.ent_passport_place = tk.Entry(
            self,
            textvariable=self.passport_place,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_citizenship = tk.Label(
            self,
            font=self.font,
            text="Državljanstvo:"
        )

        self.citizenship = tk.StringVar()
        self.ent_citizenship = tk.Entry(
            self,
            textvariable=self.citizenship,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_NPIN.place(rely=0.1, relx=0.05, anchor="nw")
        self.ent_NPIN.place(rely=0.14, relx=0.05, anchor="nw")

        self.lbl_NPIN_expire.place(rely=0.1, relx=0.55, anchor="nw")
        self.calendar_NPIN_expire.place(rely=0.14, relx=0.55, anchor="nw")

        self.chk_NPIN_permament.place(rely=0.22, relx=0.55, anchor="nw")

        self.lbl_NPIN_place.place(rely=0.3, relx=0.05, anchor="nw")
        self.ent_NPIN_place.place(rely=0.34, relx=0.05, anchor="nw")

        self.lbl_passport.place(rely=0.42, relx=0.05, anchor="nw")
        self.ent_passport.place(rely=0.46, relx=0.05, anchor="nw")

        self.lbl_passport_expire.place(rely=0.42, relx=0.55, anchor="nw")
        self.calendar_passport_expire.place(rely=0.46, relx=0.55, anchor="nw")

        self.chk_passport_exists.place(rely=0.54, relx=0.55, anchor="nw")

        self.lbl_passport_place.place(rely=0.62, relx=0.05, anchor="nw")
        self.ent_passport_place.place(rely=0.66, relx=0.05, anchor="nw")

        self.lbl_citizenship.place(rely=0.74, relx=0.05, anchor="nw")
        self.ent_citizenship.place(rely=0.78, relx=0.05, anchor="nw")

    def ValidateNumbers(self, P):
        if P.isdigit() or P == "":
            return True

    def UpdateValues(self, values: sqlTypes.ShooterPINInfo):
        self.NPIN.set(values['OI'])
        self.calendar_NPIN_expire.set_date(datetime.strptime(values['OIDatum'], "%Y-%m-%d").strftime("%d. %m. %Y."))
        self.NPIN_permament.set(values['OITrajna'])
        self.passport.set(values['Putovnica'])
        self.calendar_passport_expire.set_date(
            datetime.strptime(values['PutovnicaDatum'], "%Y-%m-%d").strftime("%d. %m. %Y.")
        )
        self.passport_exists.set(values['PutovnicaPostoji'])
        self.passport_place.set(values['PutovnicaMjesto'])
        self.citizenship.set(values['Drzavljanstvo'])

    def get_values(self) -> sqlTypes.ShooterPINInfo:
        values: sqlTypes.ShooterPINInfo = {
            "id": 0,
            "OI": self.NPIN.get(),
            "OIDatum": str(self.calendar_NPIN_expire.get_date()),
            "OITrajna": self.NPIN_permament.get(),
            "OIMjesto": self.NPIN_place.get(),
            "Putovnica": self.passport.get(),
            "PutovnicaDatum": (self.calendar_passport_expire.get_date()),
            "PutovnicaPostoji": self.passport_exists.get(),
            "PutovnicaMjesto": self.passport_place.get(),
            "Drzavljanstvo": self.citizenship.get()
        }
        return values

    def CheckNPIN(self):
        if self.calendar_NPIN_expire.get_date() > self.controller.current_date:
            self.lbl_NPIN_expire.configure(bg="green")
        else:
            self.lbl_NPIN_expire.configure(bg="red")

    def CheckNPINPermanent(self):
        if self.NPIN_permament.get():
            self.calendar_NPIN_expire.configure(state="disabled")
        else:
            self.calendar_NPIN_expire.configure(state="normal")

    def CheckPassport(self):
        if self.passport_exists.get():
            self.calendar_passport_expire.configure(state="disabled")
            self.ent_passport.configure(state="disabled")
            self.ent_passport_place.configure(state="disabled")
        else:
            self.calendar_passport_expire.configure(state="normal")
            self.ent_passport.configure(state="normal")
            self.ent_passport_place.configure(state="normal")
