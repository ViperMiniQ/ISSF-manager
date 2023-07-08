import tkinter as tk
import Fonts
import sqlTypes


class ShooterInfoContact(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.font = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]

        self.lbl_phone_house = tk.Label(
            self,
            text="Telefon kućni:",
            font=self.font
        )

        self.phone_house = tk.StringVar()
        self.ent_phone_house = tk.Entry(
            self,
            textvariable=self.phone_house,
            font=self.font,
            width=20,
            bd=3
        )

        self.lbl_phone_work = tk.Label(
            self,
            text="Telefon posao:",
            font=self.font
        )

        self.phone_work = tk.StringVar()
        self.ent_phone_work = tk.Entry(
            self,
            textvariable=self.phone_work,
            font=self.font,
            width=20,
            bd=3
        )

        self.lbl_mobile1 = tk.Label(
            self,
            font=self.font,
            text="Mobitel 1:"
        )

        self.mobile1 = tk.StringVar()
        self.ent_mobile1 = tk.Entry(
            self,
            textvariable=self.mobile1,
            font=self.font,
            width=20,
            bd=3
        )

        self.lbl_mobile2 = tk.Label(
            self,
            font=self.font,
            text="Mobitel 2:"
        )

        self.mobile2 = tk.StringVar()
        self.ent_mobile2 = tk.Entry(
            self,
            textvariable=self.mobile2,
            font=self.font,
            width=20,
            bd=3
        )

        self.lbl_email = tk.Label(
            self,
            text="E-mail:",
            font=self.font
        )

        self.email = tk.StringVar()
        self.ent_email = tk.Entry(
            self,
            textvariable=self.email,
            font=self.font,
            width=32,
            bd=3
        )

        self.lbl_phone_house.place(relx=0.1, rely=0.1, anchor="nw")
        self.ent_phone_house.place(relx=0.1, rely=0.14, anchor="nw")

        self.lbl_phone_work.place(relx=0.1, rely=0.22, anchor="nw")
        self.ent_phone_work.place(relx=0.1, rely=0.26, anchor="nw")

        self.lbl_mobile1.place(relx=0.1, rely=0.42, anchor="nw")
        self.ent_mobile1.place(relx=0.1, rely=0.46, anchor="nw")

        self.lbl_mobile2.place(relx=0.1, rely=0.54, anchor="nw")
        self.ent_mobile2.place(relx=0.1, rely=0.58, anchor="nw")

        self.lbl_email.place(relx=0.1, rely=0.66, anchor="nw")
        self.ent_email.place(relx=0.1, rely=0.7, anchor="nw")

    def update_values(self, values: sqlTypes.ShooterContactInfo):
        self.phone_house.set(values["TelefonKuca"])
        self.phone_work.set(values["TelefonPosao"])
        self.mobile1.set(values["Mobitel1"])
        self.mobile2.set(values["Mobitel2"])
        self.email.set(values["Email"])

    def get_values(self) -> sqlTypes.ShooterContactInfo:
        values: sqlTypes.ShooterContactInfo = {
            "id": 0,
            "TelefonKuca": self.phone_house.get(),
            "TelefonPosao": self.phone_work.get(),
            "Mobitel1": self.mobile1.get(),
            "Mobitel2": self.mobile2.get(),
            "Email": self.email.get()
        }
        return values
