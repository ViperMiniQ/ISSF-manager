import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from dateutil.relativedelta import relativedelta
import Colors
import ScrollableFrame
import Notification
import Fonts
import sqlTypes
from Calendar import NotificationCalendar
from datetime import datetime, timedelta
import KeepAspectRatio
from CustomWidgets import MenuTreeview
import ApplicationProperties
from dbcommands_rewrite import DBGetter
import Tools


class Start(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.up = True

        self.x = 800
        self.y = 450

        self.notification_colors_json_file = ApplicationProperties.LOCATION + "/Config/NotificationColors.json"

        self.txt_doctor_expires = "Liječnički ističe"
        self.txt_doctor_expired = "Liječnički je istekao"
        self.txt_NPIN_expires = "Osobna ističe"
        self.txt_NPIN_expired = "Osobna je istekla"
        self.txt_air_cylinder_expires = "Rok uporabe zračnog cilindra pri kraju"
        self.txt_air_cylinder_expired = "Rok uporabe zračnog cilindra je istekao"

        self.doctor_expires = []
        self.doctor_expired = []
        self.NPIN_expires = []
        self.NPIN_expired = []
        self.others = []
        self.birthdays = []
        self.air_cylinders = []

        self.upcoming_competitions = []
        self.elapsed_competitions = []

        self.doctor_day = 30
        self.NPIN_day = 30
        self.competitions_day = 30
        self.air_cylinder_day = 180
        self.reminders = {}

        self.load_colors()

        self.reminder_dict = []
        self.calendar_notifications = []

        self.font = Fonts.fonts2["StartPage"]["labels"]["font"]

        self.frame_control_buttons = tk.Frame(self)
        self.frame_reminders = ScrollableFrame.Vertical(self)
        self.frame_reminders.grid_propagate(False)

        for x in range(0, 10, 1):
            self.frame_control_buttons.columnconfigure(x, weight=1, uniform="frame_control_buttons_columns")
        self.frame_control_buttons.rowconfigure(0, weight=1)
        self.frame_control_buttons.grid_propagate(False)
        
        self.btn_show_only_reminders = tk.Button(
            self.frame_control_buttons,
            text=u"\u25b2",
            font=self.font,
            command=lambda: self.UpDownReminder()
        )

        self.btn_new_reminder = tk.Button(
            self.frame_control_buttons,
            text="+",
            bg="lime",
            fg="black",
            font=self.font,
            command=self.new_reminder
        )

        self.frame_reminders.scrollable_frame.grid_columnconfigure(0, weight=1, uniform="columns")
        self.frame_reminders.scrollable_frame.grid_columnconfigure(1, weight=10, uniform="columns")
        self.frame_reminders.scrollable_frame.grid_columnconfigure(2, weight=1, uniform="columns")

        self.row = 0

        self.grid_propagate(False)
        self.rowconfigure(0, weight=1, uniform="row")
        self.rowconfigure(1, weight=6, uniform="row")
        self.rowconfigure(2, weight=9, uniform="row")

        self.columnconfigure(0, weight=1, uniform="column")
        self.columnconfigure(1, weight=1, uniform="column")
        self.columnconfigure(2, weight=2, uniform="column")

        self.btn_show_only_reminders.grid(row=0, column=0, sticky="nsew")
        self.btn_new_reminder.grid(row=0, column=1, sticky="nsew")

        self.frame_info = StarPageList(self, self, on_change_notif_func=self.load_notifications)

        self.empty_frame = tk.Frame(self, bg="red")
        self.empty_frame.propagate(False)

        self.frame_info.grid(row=1, column=0, sticky="nsew", columnspan=2)

        self.frame_reminders.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.calendar = NotificationCalendar(self)
        self.calendar.grid(row=0, rowspan=2, column=2, sticky="nsew")
        self.frame_control_buttons.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.load_notifications()

    def new_reminder(self):
        ask = Notification.AddNotification(self)
        ask.wait_window()
        if ask.saved:
            self.load_notifications()

    def load_colors(self):
        self.reload_reminders()

    def load_air_cylinders_to_expire(self):
        air_cylinders = DBGetter.get_air_cylinders()
        for air_cylinder in air_cylinders:
            date = Tools.string_to_datetime_date(air_cylinder['date_expire'])
            if date < ApplicationProperties.CURRENT_DATE:
                continue
            if date > ApplicationProperties.CURRENT_DATE + timedelta(days=self.air_cylinder_day):
                continue
            cylinder_expire: sqlTypes.Notification = {
                "id": 0,
                "title": f"{air_cylinder['manufacturer']} ({air_cylinder['serial_no']})",
                "text": self.txt_air_cylinder_expires,
                "date": air_cylinder['date_expire'],
                "bg": "grey",
                "fg": "black",
                "type": "Zračni cilindar"
            }
            self.air_cylinders.append(cylinder_expire)

    def load_NPIN_about_to_expire(self):
        shooters_with_NPIN_about_to_expire = DBGetter.get_shooter_with_NPIN_about_to_expire(self.NPIN_day)
        for shooter in shooters_with_NPIN_about_to_expire:
            NPIN_expires: sqlTypes.Notification = {
                "id": 0,
                "title": f"{shooter['Ime']} {shooter['Prezime']}",
                "text": self.txt_NPIN_expires,
                "date": shooter['DatumIstekaOI'],
                "bg": Colors.colors["Notifications"]["NPIN_expiring"]["bg"],
                "fg": Colors.colors["Notifications"]["NPIN_expiring"]["fg"],
                "type": "Osobna ističe"
            }
            self.NPIN_expires.append(NPIN_expires)

    def load_NPIN_expired(self):
        shooters_with_NPIN_expired = DBGetter.get_shooters_with_expired_NPIN()
        for shooter in shooters_with_NPIN_expired:
            NPIN_expired: sqlTypes.Notification = {
                "id": 0,
                "title": f"{shooter['Ime']} {shooter['Prezime']}",
                "text": self.txt_NPIN_expired,
                "date": shooter['DatumIstekaOI'],
                "bg": Colors.colors["Notifications"]["NPIN_expired"]["bg"],
                "fg": Colors.colors["Notifications"]["NPIN_expired"]["fg"],
                "type": "Osobna istekla"
            }
            self.NPIN_expired.append(NPIN_expired)

    def load_doctor_expired(self):
        shooters_with_expired_doctors = DBGetter.get_registered_shooters_with_expired_doctors() \
                                        + DBGetter.get_registered_shooters_with_no_doctors()
        for shooter in shooters_with_expired_doctors:
            doctors_expired: sqlTypes.Notification = {
                "id": 0,
                "title": f"{shooter['Ime']} {shooter['Prezime']}",
                "text": self.txt_doctor_expired,
                "date": shooter['DatumIstekaLijecnickog'],
                "bg": Colors.colors["Notifications"]["doctor_expired"]["bg"],
                "fg": Colors.colors["Notifications"]["doctor_expired"]["fg"],
                "type": "Liječnički istekao"
            }
            self.doctor_expired.append(doctors_expired)

    def load_doctor_about_to_expire(self):
        shooters_whose_doctors_is_about_to_expire = DBGetter.get_registered_shooters_with_doctors_about_to_expire(
            self.doctor_day
        )
        for shooter in shooters_whose_doctors_is_about_to_expire:
            doctors_expires: sqlTypes.Notification = {
                "id": 0,
                "title": f"{shooter['Ime']} {shooter['Prezime']}",
                "text": self.txt_doctor_expires,
                "date": shooter['DatumIstekaLijecnickog'],
                "bg": Colors.colors["Notifications"]["doctor_expiring"]["bg"],
                "fg": Colors.colors["Notifications"]["doctor_expiring"]["fg"],
                "type": "Liječnički ističe"
            }
            self.doctor_expires.append(doctors_expires)

    def load_other(self):
        other_reminders = DBGetter.get_active_other_reminders()
        for reminder in other_reminders:
            other: sqlTypes.Notification = {
                "id": reminder['id'],
                "title": reminder['Naslov'],
                "date": reminder['Datum'],
                "text": reminder['Tekst'],
                "bg": Colors.colors["Notifications"]["other"]["bg"],
                "fg": Colors.colors["Notifications"]["other"]["fg"],
                "type": "other"
            }
            self.others.append(other)

    def load_birthdays(self):
        birthdays = DBGetter.get_shooters_birthdays()
        for b in birthdays:
            b_date = datetime.strptime(b['Datum'], Tools.sql_date_format).date()
            age = relativedelta(ApplicationProperties.CURRENT_DATE, b_date)
            self.birthdays.append(
                {
                    "id": 0,
                    "title": f"{b['Ime']} {b['Prezime']}",
                    "date": str(b_date + relativedelta(years=age.years + 1)),
                    "text": "Uskoro ima rođendan!",
                    "bg": Colors.colors["Notifications"]["rođendan"]["bg"],
                    "fg": Colors.colors["Notifications"]["rođendan"]["fg"],
                    "type": "Rođendan"
                }
            )

    def fill_competitions(self):
        competitions = DBGetter.get_competitions(state="all")
        for competition in competitions:
            values: sqlTypes.Notification = {
                "id": 0,
                "title": competition['Naziv'],
                "text": competition['Napomena'],
                "date": competition['Datum'],
                "bg": "lime",
                "fg": "black",
                "type": "Natjecanja"
            }
            if datetime.strptime(competition['Datum'], "%Y-%m-%d") >= datetime.now():
                self.upcoming_competitions.append(values)
                continue
            self.elapsed_competitions.append(values)

    def WindowWhereDate(self, date):
        notifications = list(
            filter(
                lambda reminder: reminder["date"] == date,
                self.NPIN_expires
                + self.NPIN_expired
                + self.doctor_expired
                + self.doctor_expires
                + self.elapsed_competitions
                + self.upcoming_competitions
                + self.others
                + self.birthdays)
        )
        if not notifications:
            return
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y.")
        notifications_window = Notification.WindowNotifications(self, date, 800, 450)
        for notification in notifications:
            notifications_window._place_reminder(
                title=notification["title"],
                text=notification["text"],
                frame_color=notification["color"],
                txt_color=notification["txt_color"]
            )
        notifications_window.wait_window()

    def clear_reminders(self):
        self.clear_all_reminders()

        self.doctor_expired.clear()
        self.doctor_expires.clear()
        self.NPIN_expired.clear()
        self.NPIN_expires.clear()

        self.others.clear()
        self.birthdays.clear()

        self.reminder_dict.clear()
        self.reminders.clear()

        self.upcoming_competitions.clear()
        self.elapsed_competitions.clear()

        self.air_cylinders.clear()

    def refresh_reminders_dicts(self):
        self.load_doctor_expired()
        self.frame_info.set_row_number("Liječnički istekao", len(self.doctor_expired))
        self.load_doctor_about_to_expire()
        self.frame_info.set_row_number("Liječnički ističe", len(self.doctor_expires))
        self.load_NPIN_expired()
        self.frame_info.set_row_number("Osobna istekla", len(self.NPIN_expired))
        self.load_NPIN_about_to_expire()
        self.frame_info.set_row_number("Osobna ističe", len(self.NPIN_expires))
        self.fill_competitions()
        self.frame_info.set_row_number("Natjecanja", len(self.upcoming_competitions))
        self.load_other()
        self.frame_info.set_row_number("Drugo", len(self.others))
        self.load_birthdays()
        self.frame_info.set_row_number("Rođendan", len(self.birthdays))
        self.load_air_cylinders_to_expire()
        self.frame_info.set_row_number("Zračni cilindar", len(self.air_cylinders))

    def update_reminders(self):
        self.load_notifications()

    def load_notifications(self):
        self.clear_reminders()
        self.refresh_reminders_dicts()
        self.frame_reminders.scrollbar.set(0, 0)
        states = self.frame_info.get_states()
        all_reminders = []
        if states["Liječnički istekao"]:
            all_reminders += self.doctor_expired
        if states["Liječnički ističe"]:
            all_reminders += self.doctor_expires
        if states["Osobna istekla"]:
            all_reminders += self.NPIN_expired
        if states["Osobna ističe"]:
            all_reminders += self.NPIN_expires
        if states["Natjecanja"]:
            all_reminders += self.upcoming_competitions
        if states["Drugo"]:
            all_reminders += self.others
        if states["Rođendan"]:
            all_reminders += self.birthdays
        if states["Zračni cilindar"]:
            all_reminders += self.air_cylinders
        self.reminders = sorted(
            all_reminders,
            key=lambda d: d['date']
        )
        self.SelectAllCalendar()
        self.reload_reminders()

    def reload_reminders(self):
        for reminder in self.reminders:
            if reminder['id']:
                self._place_reminder(reminder, True)
                continue
            self._place_reminder(reminder, False)

    def do_nothing(self):
        pass
        
    def _place_reminder(self, details: sqlTypes.Notification, deletable: bool = False):
        if not deletable:
            reminder = Notification.Notification(
                self.frame_reminders.scrollable_frame,
                title=details['title'],
                text=details['text'],
                date=Tools.SQL_date_format_to_croatian(details['date']),
                bg=details['bg'],
                fg=details['fg'],
                font=tkFont.Font(family="Calibri", size=14),
                bd=10
            )
        else:
            reminder = Notification.NotificationDeletable(
                self.frame_reminders.scrollable_frame,
                title=details['title'],
                text=details['text'],
                date=Tools.SQL_date_format_to_croatian(details['date']),
                bg=details['bg'],
                fg=details['fg'],
                font=tkFont.Font(family="Calibri", size=14),
                notif_id=details['id'],
                bd=10
            )

        reminder.grid(
            row=self.row,
            column=1,
            sticky="nsew",
            pady=10
        )

        self.row += 1
        KeepAspectRatio.subscribe(reminder)
        reminder.keep_aspect_ratio()

    def clear_all_reminders(self):
        for child in self.frame_reminders.scrollable_frame.winfo_children():
            child.destroy()

    def UpDownReminder(self):       
        if self.up:
            self.calendar.grid_forget()
            self.frame_reminders.grid_forget()
            self.frame_info.grid_forget()
            self.frame_reminders.grid(row=1, rowspan=2, column=0, columnspan=3, sticky="nsew")
            self.btn_show_only_reminders.configure(text=u"\u25bc")
        else:
            self.frame_reminders.grid_forget()
            self.calendar.grid(row=0, rowspan=2, column=2, sticky="nsew")
            self.frame_reminders.grid(row=2, column=0, columnspan=3, sticky="nsew")
            self.calendar.update()
            self.frame_info.grid(row=1, column=0, sticky="nsew", columnspan=2)
            self.btn_show_only_reminders.configure(text=u"\u25b2")
        self.up = not self.up
        self.update()
        self.update_idletasks()

    def SelectAllCalendar(self):
        self.calendar_notifications = []
        self.calendar.UpdateDates(
            self.NPIN_expired
            + self.doctor_expired
            + self.upcoming_competitions
            + self.elapsed_competitions
            + self.others
        )

    def update_all(self):
        self.row = 0
        self.clear_all_reminders()
        self.load_colors()
        self.load_notifications()


class StarPageList(tk.Frame):
    def __init__(self, parent, controller, on_change_notif_func=None, bg: str = "grey"):
        tk.Frame.__init__(self, parent, bg=bg)
        self.parent = parent
        self.controller = controller

        KeepAspectRatio.subscribe(self)

        self.selected_symbol = u"\u2714"
        self.not_selected_symbol = ""
        self.partially_selected = u"\u2610"

        self.notif_func = on_change_notif_func

        self.pack_propagate(False)

        self.treeview_style = ttk.Style()
        self.treeview_style.configure("StartPage.Treeview", background="grey")

        self.tree = MenuTreeview(self, style="StartPage.Treeview", columns=["number", "active"], show="tree")

        self.scr_tree_vertical = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scr_tree_vertical.set)

        self.root_tree_item_font = Fonts.fonts2["StartPage"]["treeview"]["root"]["font"]
        self.node_tree_item_font = Fonts.fonts2["StartPage"]["treeview"]["nodes"]["font"]

        self.scr_tree_vertical.pack(side="right", fill="y")
        self.tree.pack(side="left", expand=True, fill="both")

        self.tree.column("number", anchor="center", width=50)
        self.tree.column("active", anchor="center", width=50)

        start_values = [0, self.selected_symbol]
        self.tree.insert("", tk.END, "Strijelci", text="Strijelci", tags="font", values=start_values)
        self.tree.insert("", tk.END, "Oružje", text="Oružje", tags="font", values=start_values)
        self.tree.insert("", tk.END, "Natjecanja", text="Natjecanja", tags="font", values=start_values)
        self.tree.insert("", tk.END, "Zračni cilindar", text="Zračni cilindar", tags="font", values=start_values)
        self.tree.insert("", tk.END, "Drugo", text="Drugo", tags="font", values=start_values)

        self.tree.insert("Strijelci", tk.END, "Osobna ističe", text="Osobna ističe", tags="child_font", values=start_values)
        self.tree.insert("Strijelci", tk.END, "Osobna istekla", text="Osobna istekla", tags="child_font", values=start_values)
        self.tree.insert("Strijelci", tk.END, "Liječnički ističe", text="Liječnički ističe", tags="child_font", values=start_values)
        self.tree.insert("Strijelci", tk.END, "Liječnički istekao", text="Liječnički istekao", tags="child_font", values=start_values)
        self.tree.insert("Strijelci", tk.END, "Rođendan", text="Rođendan", tags="child_font", values=start_values)
        self.tree.insert("Oružje", tk.END, "Zračno", text="Zračno", tags="child_font", values=start_values)
        self.tree.insert("Oružje", tk.END, "Vatreno", text="Vatreno", tags="child_font", values=start_values)
        self.tree.insert("Zračno", tk.END, "ZračnoPuška", text="Puška", tags="child_font", values=start_values)
        self.tree.insert("Zračno", tk.END, "ZračnoPištolj", text="Pištolj", tags="child_font", values=start_values)
        self.tree.insert("Vatreno", tk.END, "VatrenoPuška", text="Puška", tags="child_font", values=start_values)
        self.tree.insert("Vatreno", tk.END, "VatrenoPištolj", text="Pištolj", tags="child_font", values=start_values)
        self.tree.insert("Oružje", tk.END, "Samostrel", text="Samostrel", tags="child_font", values=start_values)

        self.tree.tag_configure("font", font=self.root_tree_item_font)
        self.tree.tag_configure("child_font", font=self.node_tree_item_font)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Prikaži", command=lambda: self.set_row_status("active"))
        self.menu.add_command(label="Ne prikazuj", command=lambda: self.set_row_status("inactive"))
        self.menu.add_separator()
        self.menu.add_command(label="Osvježi", command=lambda: self.controller.update_reminders())

        self.tree.bind("p", lambda event, c="active": self.set_row_status(c))
        self.tree.bind("P", lambda event, c="active": self.set_row_status(c))
        self.tree.bind("n", lambda event, c="inactive": self.set_row_status(c))
        self.tree.bind("N", lambda event, c="inactive": self.set_row_status(c))

        self.tree.assign_menu(self.menu)

        self.tree.set("Strijelci", column="number", value=13)
        self.tree.set("Liječnički ističe", column="number", value=113)

        self.keep_aspect_ratio()

    def get_states(self) -> dict:
        # recursion ?
        return {
            "Osobna ističe": True if self.tree.set(item="Osobna ističe", column="active") == self.selected_symbol else False,
            "Osobna istekla": True if self.tree.set(item="Osobna istekla", column="active") == self.selected_symbol else False,
            "Liječnički ističe": True if self.tree.set(item="Liječnički ističe", column="active") == self.selected_symbol else False,
            "Liječnički istekao": True if self.tree.set(item="Liječnički istekao", column="active") == self.selected_symbol else False,
            "Natjecanja": True if self.tree.set(item="Natjecanja", column="active") == self.selected_symbol else False,
            "Drugo": True if self.tree.set(item="Drugo", column="active") == self.selected_symbol else False,
            "Rođendan": True if self.tree.set(item="Rođendan", column="active") == self.selected_symbol else False,
            "Zračni cilindar": True if self.tree.set(item="Zračni cilindar", column="active") == self.selected_symbol else False
        }

    def notify(self):
        if self.notif_func is not None:
            self.notif_func()

    def check_item_children_status(self, item):
        """Returns True if all are equal, False if not"""
        if not self.tree.get_children(item):
            return
        first_child = self.tree.get_children(item)[0]
        symbol = self.tree.set(item=first_child, column="active")
        for child in self.tree.get_children(item):
            if not self.tree.set(item=child, column="active") == symbol:
                return False
        return True

    def go_up_tree_set_status(self, item, symbol: str):
        self.tree.set(item=item, column="active", value=symbol)
        if not self.tree.parent(item):
            return
        self.go_up_tree_set_status(item=self.tree.parent(item), symbol=symbol)

    def go_down_tree_set_status(self, item, symbol: str):
        if not self.tree.get_children(item):
            return
        for child in self.tree.get_children(item):
            self.tree.set(item=child, column="active", value=symbol)
            self.go_down_tree_set_status(child, symbol)

    def parent_item_has_children(self, item):
        if self.tree.get_children(item):
            return True
        return False

    def child_item_parent_not_root(self, item):
        """If the item is at root position, returns False, else returns True"""
        if self.tree.parent(item):
            return True
        return False

    def get_children_number_sum(self, item) -> int:
        if not self.tree.get_children(item):
            return 0
        int_sum: int = 0  # sum is a built-in name...
        for child in self.tree.get_children(item):
            int_sum += int(self.tree.set(item=child, column="number"))
        return int_sum

    def test_set_numbers(self, item):
        if self.tree.get_children(item):
            for child in self.tree.get_children(item):
                self.test_set_numbers(child)
        else:
            return
        self.tree.set(item=item, column="number", value=self.get_children_number_sum(item))

    def test_set_statuses(self, item):
        if self.tree.get_children(item):
            for child in self.tree.get_children(item):
                self.test_set_statuses(child)
        else:
            return
        if self.check_item_children_status(item):
            self.tree.set(item=item, column="active",
                          value=self.tree.set(item=self.tree.get_children(item)[0], column="active"))
        else:
            self.tree.set(item=item, column="active", value=self.partially_selected)

    def set_row_status(self, status: str):
        if not self.tree.focus():
            return
        if status == "active":
            self.tree.set(item=self.tree.focus(), column="active", value=self.selected_symbol)
            if self.parent_item_has_children(self.tree.focus()):
                self.go_down_tree_set_status(self.tree.focus(), self.selected_symbol)

        elif status == "inactive":
            self.tree.set(item=self.tree.focus(), column="active", value=self.not_selected_symbol)
            if self.parent_item_has_children(self.tree.focus()):
                self.go_down_tree_set_status(self.tree.focus(), self.not_selected_symbol)
        self.test_set_statuses("")
        self.notify()

    def set_row_number(self, rowID, value: int):
        self.tree.set(item=rowID, column="number", value=value)
        self.test_set_numbers("")

    def get_row_status(self, rowID):
        self.tree.set(item=rowID, column="active")

    def get_row_value(self, rowID):
        self.tree.set(item=rowID, column="number")

    def do_nothing(self):
        pass

    def set_doctor_expires(self, value: int):
        self.tree.set("Liječnički ističe", column="number", value=value)

    def set_doctor_expired(self, value: int):
        self.tree.set("Liječnički istekao", column="number", value=value)

    def set_NPIN_expires(self, value: int):
        self.tree.set("Osobna ističe", column="number", value=value)

    def set_NPIN_expired(self, value: int):
        self.tree.set("Osobna istekla", column="number", value=value)

    def set_tree_items_height(self, height: int):
        self.treeview_style.configure("StartPage.Treeview", rowheight=height, indicatorsize='100')
        self.treeview_style.theme_use()

    def open_tree_child(self, item):
        self.tree.item(item, open=True)

    def tree_open(self, event):
        self.open_tree_child(self.tree.focus())

    def keep_aspect_ratio(self):
        self.set_tree_items_height(int(self.root_tree_item_font.metrics("linespace") * 1.1))
