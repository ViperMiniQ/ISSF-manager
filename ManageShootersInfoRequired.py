import tkinter as tk
import Tools
from CustomWidgets import CustomBox, DateEntry2
import Fonts
import sqlTypes


class ShooterRequiredInformation(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.font = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]

        self.validate_numbers = (self.register(self.ValidateNumbers))

        # <GRID> #

        for x in range(0, 24, 1):
            self.grid_rowconfigure(x,weight=1)
        self.grid_columnconfigure(0,weight=1, minsize=10)
        self.grid_columnconfigure(1,weight=8, minsize=80)
        for y in range(2, 4, 1):
            self.grid_columnconfigure(y,weight=5)
        self.grid_columnconfigure(4,weight=3)
        self.grid_columnconfigure(5,weight=1, minsize=10)

        # </GRID> #

        self.lbl_lastname = tk.Label(
            self,
            text="Prezime:",
            font=self.font,
        )

        self.lastname = tk.StringVar()
        self.ent_lastname = tk.Entry(
            self,
            textvariable=self.lastname,
            font=self.font,
            width=16,
            bd=3
        )

        self.lbl_name = tk.Label(
            self,
            text="Ime:",
            font=self.font
        )

        self.name = tk.StringVar()

        self.ent_name = tk.Entry(
            self,
            textvariable=self.name,
            font=self.font,
            width=16,
            bd=3
        )

        self.lbl_sex = tk.Label(
            self,
            text="Spol:",
            font=self.font
        )

        self.sex = tk.StringVar()

        self.cbx_sex = CustomBox(
            self,
            values=["Muško", "Žensko"],
            justify="center",
            width=7,
            font=self.font,
            textvariable=self.sex
        )

        self.lbl_PIN = tk.Label(
            self,
            text="OIB:",
            font=self.font
        )

        self.PIN = tk.StringVar()
        self.ent_PIN = tk.Entry(
            self,
            textvariable=self.PIN,
            font=self.font,
            width=15,
            validatecommand=(self.validate_numbers, "%P"),
            bd=3
        )

        self.lbl_date_of_birth = tk.Label(
            self,
            text="Datum rođenja:",
            font=self.font
        )

        self.calendar_date_of_birth = DateEntry2(
            self,
            font=self.font,
            selectmode="day",
            locale="hr_HR",
            cursor="hand1",
            state="readonly"
        )


        self.lbl_place_of_birth = tk.Label(
            self,
            text="Mjesto rođenja:",
            font=self.font
        )

        self.place_of_birth = tk.StringVar()
        self.ent_place_of_birth = tk.Entry(
            self,
            textvariable=self.place_of_birth,
            font=self.font,
            width=35,
            bd=3
        )

        self.lbl_address = tk.Label(
            self,
            text="Adresa:",
            font=self.font
        )

        self.address = tk.StringVar()
        self.ent_address = tk.Entry(
            self,
            textvariable=self.address,
            font=self.font,
            width=35,
            bd=3
        )

        self.lbl_place_of_residence = tk.Label(
            self,
            text="Mjesto stanovanja:",
            font=self.font
        )

        self.place_of_residence = tk.StringVar()
        self.ent_place_of_residence = tk.Entry(
            self,
            textvariable=self.place_of_residence,
            font=self.font,
            width=35,
            bd=3
        )

        self.lbl_HSS = tk.Label(
            self,
            text="HSS iskaznica:",
            font=self.font
        )

        self.HSS = tk.StringVar()
        self.ent_HSS = tk.Entry(
            self,
            textvariable=self.HSS,
            font=self.font,
            width=10,
            validatecommand=(self.validate_numbers, "%P"),
            bd=3
        )

        self.ent_lastname.place(relx=0.05, rely=0.05, anchor="nw")
        self.lbl_lastname.place(relx=0.05, rely=0.01, anchor="nw")

        self.ent_name.place(relx=0.55, rely=0.05, anchor="nw")
        self.lbl_name.place(relx=0.55, rely=0.01, anchor="nw")

        self.lbl_sex.place(relx=0.05, rely=0.13, anchor="nw")
        self.cbx_sex.place(relx=0.05, rely=0.17, anchor="nw")

        self.lbl_PIN.place(relx=0.55, rely=0.13, anchor="nw")
        self.ent_PIN.place(relx=0.55, rely=0.17, anchor="nw")

        self.lbl_date_of_birth.place(relx=0.05, rely=0.25, anchor="nw")
        self.calendar_date_of_birth.place(relx=0.05, rely=0.29, anchor="nw")

        self.lbl_place_of_birth.place(relx=0.05, rely=0.37, anchor="nw")
        self.ent_place_of_birth.place(relx=0.05, rely=0.41, anchor="nw")

        self.lbl_address.place(relx=0.05, rely=0.49, anchor="nw")
        self.ent_address.place(relx=0.05, rely=0.53, anchor="nw")

        self.lbl_place_of_residence.place(relx=0.05, rely=0.61, anchor="nw")
        self.ent_place_of_residence.place(relx=0.05, rely=0.65, anchor="nw")

        self.lbl_HSS.place(relx=0.05, rely=0.73, anchor="nw")
        self.ent_HSS.place(relx=0.05, rely=0.77, anchor="nw")

    def UpdateValues(self, shooter_required_info: sqlTypes.ShooterRequiredInfo):
        self.name.set(shooter_required_info['Ime'])
        self.lastname.set(shooter_required_info['Prezime'])
        self.sex.set(shooter_required_info['Spol'])
        self.PIN.set(shooter_required_info['Oib'])
        self.calendar_date_of_birth.set_date(Tools.SQL_date_format_to_croatian(shooter_required_info['Datum']))
        self.place_of_birth.set(shooter_required_info['MjestoRodjenja'])
        self.address.set(shooter_required_info['Adresa'])
        self.place_of_residence.set(shooter_required_info['MjestoStanovanja'])
        self.HSS.set(shooter_required_info['HSS'])

    def get_values(self) -> sqlTypes.ShooterRequiredInfo:
        required_info: sqlTypes.ShooterRequiredInfo = {
            "id": 0,
            "Ime": self.name.get(),
            "Prezime": self.lastname.get(),
            "Spol": self.sex.get(),
            "Oib": self.PIN.get(),
            "Datum": str(self.calendar_date_of_birth.get_date()),
            "MjestoRodjenja": self.place_of_birth.get(),
            "Adresa": self.address.get(),
            "MjestoStanovanja": self.place_of_residence.get(),
            "HSS": self.HSS.get()
        }
        return required_info

    def ValidateNumbers(self, P):
        if P.isdigit() or P == "":
            return True
