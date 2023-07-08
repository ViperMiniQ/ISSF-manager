import tkinter as tk
from CustomWidgets import DateEntry2
import tkinter.font as tkFont
import Changes
from dbcommands_rewrite import DBUpdate, DBAdder


class AddNotification(tk.Toplevel):
    def __init__(self, master, date=None, title: str = "", lock_title: bool = False):
        tk.Toplevel.__init__(self, master)
        self.dictionary = {}

        self.saved = False

        x = 800
        y = 400
        x_min = 500
        y_min = 250
        self.aspect = x/y

        self.geometry("{}x{}".format(x, y))
        self.minsize(x_min, y_min)
        self.grid_propagate(False)
        self.title("Dodaj obavijest")
        self.font = tkFont.Font(size=14)

        self.frame_txt = tk.Frame(self)
        ###########################################
        #                                         #
        #   Naslov:   xxxxxxxxxxxxxxxxxx          #
        #                                         #
        #   Tekst:    xxxxxxxxxxxxxxxxxx          #
        #             xxxxxxxxxxxxxxxxxx          #
        #             xxxxxxxxxxxxxxxxxx          #
        #                                         #
        #   Datum:    DD-MM-YYYY                  #
        #                                         #
        ###########################################

        self.columnconfigure(0, weight=1, uniform="columns")
        self.columnconfigure(1, weight=5, uniform="columns")
        self.columnconfigure(2, weight=3, uniform="columns")
        self.columnconfigure(3, weight=3, uniform="columns")
        self.columnconfigure(4, weight=2, uniform="columns")
        self.columnconfigure(5, weight=1, uniform="columns")

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=3, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=9, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")
        self.rowconfigure(5, weight=3, uniform="rows")
        self.rowconfigure(6, weight=1, uniform="rows")
        self.rowconfigure(7, weight=2, uniform="rows")
        self.rowconfigure(8, weight=1, uniform="rows")

        self.lbl_title = tk.Label(
            self,
            text="Naslov: ",
            font=self.font
        )

        self.lbl_txt = tk.Label(
            self,
            text="Tekst:",
            font=self.font
        )

        self.lbl_date = tk.Label(
            self,
            text="Datum:",
            font=self.font
        )

        self.ent_title = tk.Entry(
            self,
            font=self.font,
            bd=3
        )

        self.txt = tk.Text(
            self.frame_txt,
            font=self.font
        )
        self.txt.pack(expand=True, fill="both")

        self.date = DateEntry2(
            self,
            selectmode="day",
            locale="hr_HR",
            font=self.font,
            state="readonly"
        )

        self.btn_add = tk.Button(
            self,
            text="Dodaj",
            bg="lime",
            font=self.font,
            command=self.save_and_exit
        )

        if date:
            self.date.set_date(date)
        if title:
            self.ent_title.insert(0, title)

        if lock_title:
            self.ent_title.configure(state="disabled")

        self.frame_txt.pack_propagate(False)
        self.grid_propagate(False)

        self.lbl_title.grid(row=1, column=1, sticky="nsew")
        self.ent_title.grid(row=1, column=2, columnspan=3, sticky="ew")
        self.lbl_txt.grid(row=3, column=1, sticky="nsew")
        self.frame_txt.grid(row=3, column=2, columnspan=3)
        self.lbl_date.grid(row=5, column=1, sticky="nsew")
        self.date.grid(row=5, column=2, sticky="w")
        self.btn_add.grid(row=7, column=4, sticky="nsew")

    def save_and_exit(self):
        """dictionary = {"title", "text", "date"}"""
        if DBAdder.add_other_reminder(
            title=self.ent_title.get(),
            text=self.txt.get("1.0", tk.END)[:-1],
            date=self.date.get_date(),
            read=False
        ):
            Changes.call_refresh_reminders()
        self.destroy()


class Notification(tk.Frame):
    def __init__(self, parent, title, text, date, bg, fg, font: tkFont.Font, notif_id: int = 0, **kwargs):
        tk.Frame.__init__(self, parent, width=100, height=80, bg=bg, **kwargs)
        self.propagate(False)

        self.notif_id = notif_id
        self.title = title
        self.text = text
        self.date = date

        self.msg_rows = self.text.count("\n") + 1

        if isinstance(font, tkFont.Font):
            self.font = font
        else:
            self.font = tkFont.Font(size=14)

        self.grid_columnconfigure(0, weight=5, uniform="columns")
        self.grid_columnconfigure(1, weight=2, uniform="columns")

        self.grid_propagate(False)

        self.lbl_text = tk.Label(
            self,
            text=self.text,
            bg=bg,
            fg=fg,
            font=self.font,
            justify="left"
        )

        self.lbl_date = tk.Label(
            self,
            text=self.date,
            bg=bg,
            fg=fg,
            anchor="w",
            font=self.font
        )

        self.lbl_title = tk.Label(
            self,
            text=self.title,
            bg=bg,
            fg=fg,
            anchor="w",
            font=self.font
        )

        self.msg_text = tk.Message(
            self,
            text=self.text,
            fg=fg,
            bg=bg
        )

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=self.msg_rows, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")

        self.lbl_title.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.lbl_text.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.lbl_date.grid(row=2, column=0, sticky="nsew")

        self.keep_aspect_ratio()

    def keep_aspect_ratio(self):
        font_height = tkFont.Font(font=self.font).metrics("linespace")
        self.configure(height=int(((self.msg_rows + 4) * font_height)))


class NotificationDeletable(Notification):
    def __init__(self, parent, title, text, date, bg, fg, font: tkFont.Font, notif_id: int, **kwargs):
        super().__init__(parent=parent, title=title, text=text, date=date, bg=bg, fg=fg, font=font, notif_id=notif_id, **kwargs)

        self.btn_action = tk.Button(
            self,
            text="Odrađeno",
            bg="black",
            fg="yellow",
            font=self.font,
            command=lambda: self.set_as_read()
        )

        self.btn_action.grid(row=2, column=1, sticky="nsew")

    def set_as_read(self):
        DBUpdate.other_reminder_read(self.notif_id)
        Changes.call_refresh_reminders()
