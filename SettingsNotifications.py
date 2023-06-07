import tkinter as tk
import Colors
import Fonts
import JSONManager
import ScrollableFrame
import ApplicationProperties
import Tools


class ModifyNotifications(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.x = 800
        self.y = 450

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=15, uniform="rows")
        self.columnconfigure(0, weight=1)

        self.font = Fonts.fonts2["ModifyNotifications"]["buttons"]["font"]
        self.notification_settings = []
        self.grid_propagate(False)

        self.frame_main = ScrollableFrame.Vertical(self)
        self.frame_main.grid(row=1, column=0, sticky="nsew")
        self.frame_main.pack_propagate(False)

        self.btn_save_settings = tk.Button(
            self,
            bg="green",
            fg="black",
            text="Spremi",
            font=self.font,
            command=lambda: self.SaveSettings()
        )

        self.btn_save_settings.grid(row=0, column=0, sticky="nsew")

        self.notification_colors_json_file = ApplicationProperties.LOCATION + "/Config/NotificationColors.json"

        key_doctor_expiring = "doctor_expiring"
        key_doctor_expired = "doctor_expired"
        key_NPIN_expiring = "NPIN_expiring"
        key_NPIN_expired = "NPIN_expired"

        self.notification_colors_json = JSONManager.load_json(self.notification_colors_json_file)
        self.notification_colors = self.notification_colors_json["notification_colors"]
        self.notification_title = self.notification_colors_json["notification_title"]
        self.notification_txt = self.notification_colors_json["notification_txt"]
        self.notification_txt_colors = self.notification_colors_json["notification_txt_colors"]
        self.notification_days = self.notification_colors_json["notification_days"]

        color_doctor_expires = self.notification_colors[key_doctor_expiring]
        color_doctor_expired = self.notification_colors[key_doctor_expired]
        color_NPIN_expires = self.notification_colors[key_NPIN_expiring]
        color_NPIN_expired = self.notification_colors[key_NPIN_expired]

        color_txt_doctor_expires = self.notification_txt_colors[key_doctor_expiring]
        color_txt_doctor_expired = self.notification_txt_colors[key_doctor_expired]
        color_txt_NPIN_expires = self.notification_txt_colors[key_NPIN_expiring]
        color_txt_NPIN_expired = self.notification_txt_colors[key_NPIN_expired]

        title_doctor_expires = self.notification_title[key_doctor_expiring]
        title_doctor_expired = self.notification_title[key_doctor_expired]
        title_NPIN_expires = self.notification_title[key_NPIN_expiring]
        title_NPIN_expired = self.notification_title[key_NPIN_expired]

        txt_doctor_expires = self.notification_txt[key_doctor_expiring]
        txt_doctor_expired = self.notification_txt[key_doctor_expired]
        txt_NPIN_expires = self.notification_txt[key_NPIN_expiring]
        txt_NPIN_expired = self.notification_txt[key_NPIN_expired]

        days_doctor_expires = self.notification_days[key_doctor_expiring]
        days_NPIN_expires = self.notification_days[key_NPIN_expiring]

        self.doctor_expiring = NotificationSettings(self.frame_main.scrollable_frame, title_doctor_expires,
                                                    txt_doctor_expires, color_doctor_expires, color_txt_doctor_expires,
                                                    key_doctor_expiring, "Prikaži obavijest ranije (dana):",
                                                    days_doctor_expires, 1, 100, True)
        self.notification_settings.append(self.doctor_expiring)
        self.notification_settings[-1].pack(side="top", expand=True, fill="x")
        self.place_empty_label()
        self.doctor_expired = NotificationSettings(self.frame_main.scrollable_frame, title_doctor_expired,
                                                   txt_doctor_expired, color_doctor_expired, color_txt_doctor_expired,
                                                   key_doctor_expired, spin=False)
        self.notification_settings.append(self.doctor_expired)
        self.notification_settings[-1].pack(side="top", expand=True, fill="x")
        self.place_empty_label()
        self.NPIN_expiring = NotificationSettings(self.frame_main.scrollable_frame, title_NPIN_expires,
                                                  txt_NPIN_expires, color_NPIN_expires, color_txt_NPIN_expires,
                                                  key_NPIN_expiring, "Prikaži obavijest ranije (dana):",
                                                  days_NPIN_expires, 1, 100, True)
        txt_NPIN_expires, self.notification_settings.append(self.NPIN_expiring)
        self.notification_settings[-1].pack(side="top", expand=True, fill="x")
        self.place_empty_label()
        self.NPIN_expired = NotificationSettings(self.frame_main.scrollable_frame, title_NPIN_expired,
                                                 txt_NPIN_expired, color_NPIN_expired, color_txt_NPIN_expired,
                                                 key_NPIN_expired, spin=False)
        self.notification_settings.append(self.NPIN_expired)
        self.notification_settings[-1].pack(side="top", expand=True, fill="x")
        self.place_empty_label()

    def SaveSettings(self):
        dictionaries = []

        for notif_setting in self.notification_settings:
            dictionaries.append(notif_setting.get_values())

        for dictionary in dictionaries:
            self.notification_colors_json["notification_colors"][dictionary["key"]] = dictionary["notification_color"]
            self.notification_colors_json["notification_txt_colors"][dictionary["key"]] = dictionary[
                "notification_txt_color"]
            self.notification_colors_json["notification_txt"][dictionary["key"]] = dictionary["notification_txt"]
            self.notification_colors_json["notification_days"][dictionary["key"]] = dictionary["days"]

        JSONManager.save_json(self.notification_colors_json_file, self.notification_colors_json)
        Colors.call_subscribers()

    def place_empty_label(self, height=1):
        lbl = tk.Label(self.frame_main.scrollable_frame, text="", font=self.font, height=height)
        lbl.pack(side="top", expand=True, fill="x")


class NotificationSettings(tk.Frame):
    def __init__(self, controller, title, entry_text, canv_color, txt_color, dict_key, spin_text="", spin_days=0,
                 spin_from=-1, spin_to=-1, spin=True, width=400, height=200):
        tk.Frame.__init__(self, controller, bg=canv_color, width=width, height=height)
        self.notification_text = tk.StringVar()
        self.days = tk.IntVar()
        self.days.set(spin_days)
        self.spin = spin
        self.spin_to = spin_to
        self.spin_from = spin_from
        self.dict_key = dict_key
        self.canv_color = canv_color
        self.txt_color = txt_color
        self.notification_text.set(entry_text)
        self.controller = controller
        self.no_of_rows = 6
        self.no_of_cols = 11
        self.font = Fonts.fonts2["NotificationSettings"]["buttons"]["font"]
        self.grid_propagate(False)

        for x in range(0, self.no_of_cols, 1):
            self.columnconfigure(x, weight=1, uniform="columns")
        for y in range(0, self.no_of_rows, 1):
            self.rowconfigure(y, weight=1, uniform="rows")

        self.lbl_title = tk.Label(self, text=title, font=self.font, bg=canv_color, fg=txt_color)
        self.ent_notification_text = tk.Entry(self, textvariable=self.notification_text, font=self.font, bd=1,
                                              fg=txt_color, bg=canv_color)
        self.lbl_spin_days = tk.Label(self, text=spin_text, font=self.font, bg=canv_color, fg=txt_color)
        self.spin_days = tk.Spinbox(self,
                                    from_=self.spin_from, to=self.spin_to, wrap=False, state="readonly",
                                    font=self.font, textvariable=self.days
        )
        self.btn_frame_color = tk.Button(
            self,
            text="Pozadinska boja",
            bd=2,
            fg="black",
            bg="white",
            font=self.font,
            command=lambda: self._change_background_color()
        )

        self.btn_text_color = tk.Button(
            self,
            text="Boja teksta",
            bd=2,
            fg="black",
            bg="white",
            font=self.font,
            command=lambda: self._change_text_color()
        )

        self.lbl_title.grid(row=0, rowspan=2, column=0, columnspan=5, sticky="nsew")
        self.ent_notification_text.grid(row=2, column=1, columnspan=5, sticky="nsew")
        self.btn_frame_color.grid(row=1, rowspan=2, column=7, columnspan=3, sticky="nsew")
        self.btn_text_color.grid(row=3, rowspan=2, column=7, sticky="nse")

        if self.spin:
            self.spin_days.grid(row=4, column=4, sticky="nsew")
            self.lbl_spin_days.grid(row=4, column=0, columnspan=4, sticky="nsew")

    def get_values(self):
        dictionary = {}
        dictionary["key"] = self.dict_key
        dictionary["notification_txt"] = self.notification_text.get()
        if self.spin:
            dictionary["days"] = int(self.spin_days.get())
        else:
            dictionary["days"] = 0
        dictionary["notification_txt_color"] = self.txt_color
        dictionary["notification_color"] = self.canv_color
        return dictionary

    def _change_text_color(self, event=None):
        color = Tools.color_picker()
        if not color:
            return
        self.lbl_title.configure(fg=color)
        self.ent_notification_text.configure(fg=color)
        self.txt_color = color

    def _change_background_color(self, event=None):
        color = Tools.color_picker()
        if not color:
            return
        self.lbl_title.configure(bg=color)
        self.configure(bg=color)
        self.ent_notification_text.configure(bg=color)
        self.canv_color = color
