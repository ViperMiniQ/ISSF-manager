from datetime import datetime
import tkinter as tk
import calendar
import Fonts
import ApplicationProperties


class Calendar(tk.Frame):
    """
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
   █   <<<   █    <<    █    mjesec godina    █    >>    █   >>>   █
   █■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
   █   PON      UTO      SRI      ČET      PET      SUB      NED   █
   █ ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ █
   █ ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀ █
   █ ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ █
   █ ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀ █
   █ ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ █
   █ ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀ █
   █ ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄ █
   █ ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀ █
   █ ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄                                              █
   █ ▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀                                              █
   ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    """
    def __init__(self, parent):
        super().__init__(parent, bg="blue")
        self.btn_dates = {}

        self.year = ApplicationProperties.CURRENT_DATE.year
        self.month = ApplicationProperties.CURRENT_DATE.month
        self.day = ApplicationProperties.CURRENT_DATE.day

        self.buttons = []

        self.rowconfigure(0, weight=1, uniform="columns")
        self.rowconfigure(1, weight=3, uniform="columns")
        self.columnconfigure(0, weight=1)

        self.font = Fonts.fonts2["Calendar"]["font"]

        # title configure
        self.frame_title = tk.Frame(self)
        self.frame_title.grid_propagate(False)
        self.frame_title.rowconfigure(0, weight=1)
        self.frame_title.rowconfigure(1, weight=5)
        self.frame_title.rowconfigure(2, weight=5)

        self.grid_propagate(False)

        for x in range(0, 15, 2):
            self.frame_title.columnconfigure(x, weight=1, uniform='title_column')
        for x in range(1, 15, 2):
            self.frame_title.columnconfigure(x, weight=5, uniform='title_column')
        # /title configure

        # buttons configure
        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.grid_propagate(False)

        for x in range(0, 15, 2):
            self.frame_buttons.columnconfigure(x, weight=1, uniform="buttons_column")
        for x in range(1, 15, 2):
            self.frame_buttons.columnconfigure(x, weight=5, uniform="buttons_column")
        for y in range(0, 12, 2):
            self.frame_buttons.rowconfigure(y, weight=1, uniform="buttons_row")
        for y in range(1, 12, 2):
            self.frame_buttons.rowconfigure(y, weight=5, uniform="buttons_row")
        # /buttons configure

        self.frame_title.grid(row=0, column=0, sticky="nsew")
        self.frame_buttons.grid(row=1, column=0, sticky="nsew")

        self.lbl_title = tk.Label(
            self.frame_title,
            font=self.font
        )

        self.btn_next_month = tk.Button(
            self.frame_title,
            text=">",
            font=self.font,
            bd=3,
            command=lambda: self._next_month()
        )

        self.btn_previous_month = tk.Button(
            self.frame_title,
            text="<",
            font=self.font,
            bd=3,
            command=lambda: self._previous_month()
        )

        self.btn_next_year = tk.Button(
            self.frame_title,
            text=">>>",
            font=self.font,
            bd=3,
            command=lambda: self._next_year()
        )

        self.btn_previous_year = tk.Button(
            self.frame_title,
            text="<<<",
            font=self.font,
            bd=3,
            command=lambda: self._previous_year()
        )

        for i, day in enumerate(list(calendar.day_abbr)):
            tk.Label(
                self.frame_title,
                text=day.upper(),
                font=self.font
            ).grid(row=2, column=(i * 2) + 1, sticky="ew")

        self.btn_previous_month.grid(row=0, column=3, sticky="ew")
        self.btn_previous_year.grid(row=0, column=1, sticky="ew")
        self.lbl_title.grid(row=0, column=5, columnspan=5, sticky="ew")
        self.btn_next_month.grid(row=0, column=11, sticky="ew")
        self.btn_next_year.grid(row=0, column=13, sticky="ew")

        self.create_day_buttons()
        self.update_title()

    def _clear_day_buttons(self):
        for widget in self.frame_buttons.winfo_children():
            widget.destroy()
        self.buttons.clear()

    def create_day_buttons(self):
        self._clear_day_buttons()

        row = 1
        column = datetime(self.year, self.month, 1).weekday() * 2 + 1  # ((7 - last_day_in_first_week) * 2) + 1
        for i in range(1, calendar.monthrange(self.year, self.month)[1], 1):
            self.buttons.append(
                tk.Button(
                    self.frame_buttons,
                    text=i,
                    bd=2,
                    anchor="center",
                    font=self.font,
                )
            )
            self.buttons[-1].grid(row=row, column=column, sticky="nsew")
            column += 2
            if column == 15:
                row += 2  # row will never overflow
                column = 1

    def _next_month(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1

        self.create_day_buttons()
        self.update_title()

    def _previous_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1

        self.create_day_buttons()
        self.update_title()

    def _previous_year(self):
        self.year -= 1

        self.create_day_buttons()
        self.update_title()

    def _next_year(self):
        self.year += 1

        self.create_day_buttons()
        self.update_title()

    def update_title(self):
        self.lbl_title.configure(text=f"{calendar.month_name[self.month].upper()} {str(self.year)}")

    @classmethod
    def get_utc_milliseconds_in_days(cls, days: int) -> int:
        return 86400000 * days

    @classmethod
    def get_month_start(cls, year: int, month: int) -> int:
        """UTC time in milliseconds"""
        return int(
            datetime(
                year=year,
                month=month,
                day=1
            ).timestamp()
        ) * 1000


class NotificationCalendar(Calendar):
    def __init__(self, parent):
        super().__init__(parent)

        self.btn_dates = []
        # self.btn_next_year.configure(
        #     command=Tools.combine_funcs(self._next_year, self.color_day_buttons)
        # )
        # self.btn_next_month.configure(
        #     command=Tools.combine_funcs(self._next_month, self.color_day_buttons)
        # )

    def _next_year(self):
        super()._next_year()
        self.color_day_buttons()

    def _next_month(self):
        super()._next_month()
        self.color_day_buttons()

    def _previous_year(self):
        super()._previous_year()
        self.color_day_buttons()

    def _previous_month(self):
        super()._previous_month()
        self.color_day_buttons()

    def color_day_buttons(self):
        for notification in self.btn_dates:
            try:
                if (int(datetime.strptime(notification["date"], '%Y-%m-%d').strftime('%m')) == self.month and
                int(datetime.strptime(notification["date"], '%Y-%m-%d').strftime('%Y')) == self.year):
                    day = int(datetime.strptime(notification["date"], '%Y-%m-%d').strftime('%d'))
                    self.buttons[day-1].configure(bg=notification["bg"])
            except Exception as e:
                pass

    def set_notifications(self, notifications):
        self.btn_dates = notifications
        self.color_day_buttons()
