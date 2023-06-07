import tkinter as tk
import tkinter.font as tkFont
import dbcommands


class ShooterNotifications(tk.Frame):
    def __init__(self, parent, sql: dbcommands.db):
        tk.Frame.__init__(self, parent)
        self.font = tkFont.Font(size=14)

        # <GRID> #
        for x in range(0, 20, 2):
            self.rowconfigure(x, weight=1, uniform="rows")
        for x in range(1, 20, 2):
            self.rowconfigure(x, weight=1, uniform="rows")
        self.columnconfigure(0, weight=1, uniform="columns")
        self.columnconfigure(1, weight=10, uniform="columns")
        self.columnconfigure(2, weight=1, uniform="columns")


        self.NPIN_alerts = tk.IntVar()
        self.chk_NPIN_alerts = tk.Checkbutton(
            self,
            text="Obavijesti za osobnu iskaznicu",
            font=self.font,
            variable=self.NPIN_alerts,
            onvalue=0,
            offvalue=1,
            command=lambda: self.__update_NPIN_alerts()
        )

        self.doctor_alerts = tk.IntVar()
        self.chk_doctor_alerts = tk.Checkbutton(
            self,
            text="Obavijesti za liječnički",
            font=self.font,
            variable=self.doctor_alerts,
            onvalue=0,
            offvalue=1,
            command=lambda: self.__update_doctor_alerts()
        )

        self.chk_NPIN_alerts.grid(row=1, column=1, sticky="w")
        self.chk_doctor_alerts.grid(row=3, column=1, sticky="w")

    def set_NPIN_alerts(self, state: bool):
        pass

    def set_doctor_alerts(self, state: bool):
        pass

    def __update_NPIN_alerts(self):
        pass

    def __update_doctor_alerts(self):
        pass

    def refresh(self):
        pass
