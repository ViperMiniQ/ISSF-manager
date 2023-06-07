import tkinter as tk
import time
from tkinter.constants import END
import tkinter.font as tkFont
import Tools
import sqlTypes
from CustomWidgets import CustomBox, DateEntry2
from dbcommands_rewrite import DBAdder, DBGetter, DBUpdate


class CompetitionsInput(tk.Toplevel):
    def __init__(self, parent, values: sqlTypes.CompetitionInfo = None, save: bool = False, modify: bool = False):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Natjecanje")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.ExitButton)
        self.modify = modify
        self.programs = DBGetter.get_programs()
        self.ent_empty_text = "Napomena:"
        self.time = time.time()
        self.save = save
        cbx_program_list = []
        for program in self.programs:
            cbx_program_list.append(program['Naziv'])

        self.geometry("800x450")
        self.minsize(720, 450)
        self.aspect_ratio = 16 / 9

        self.font = tkFont.Font(size=14)

        self.title = tk.StringVar()
        self.place = tk.StringVar()
        self.address = tk.StringVar()
        self.program = tk.StringVar()
        self.hss_id = tk.IntVar()

        self.cadets = tk.IntVar()
        self.juniors = tk.IntVar()
        self.seniors = tk.IntVar()
        self.veterans = tk.IntVar()

        # 1    2       2         2           2          2        1
        # 1
        # 3  Naziv:          xxxxxxxxxx
        # 1
        # 3  Mjesto:         xxxxxxxxxxxxx
        # 1
        # 3  Adresa:         xxxxxxxxxxxxxxxxxxx
        # 1
        # 3  Datum:          xxxxxxxxx
        # 1
        # 3  Kategorija:     o kadeti    o juniori   o seniori
        # 1
        #   ----------------------------------------------------
        #   | Napomena:                                        |
        # 5 |                                                  |
        #   |                                                  |
        #   ----------------------------------------------------

        self.grid_propagate(False)
        self.resizable(False, False)
        self.zero = 0

        self.frame_main = tk.Frame(self)
        self.frame_note = tk.Frame(self)
        self.frame_buttons = tk.Frame(self)

        for x in range(0, 6, 1):
            self.frame_main.columnconfigure(x, weight=5, uniform="main_columns")
        for y in range(0, 13, 2):
            self.frame_main.rowconfigure(y, weight=1, uniform="main_rows")
        for y in range(1, 13, 2):
            self.frame_main.rowconfigure(y, weight=3, uniform="main_rows")

        for x in range(0, 5, 1):
            self.frame_buttons.columnconfigure(x, weight=1, uniform="buttons_columns")
        for y in range(0, 3, 1):
            self.frame_buttons.rowconfigure(y, weight=1, uniform="buttons_rows")

        self.categories = [tk.IntVar(), tk.IntVar(), tk.IntVar()]

        self.lbl_title = tk.Label(
            self.frame_main,
            text="Naziv:",
            anchor="e",
            font=self.font,
        )

        self.ent_title = tk.Entry(
            self.frame_main,
            bd=2,
            font=self.font,
            textvariable=self.title,
        )

        self.lbl_place = tk.Label(
            self.frame_main,
            text="Mjesto:",
            anchor="e",
            font=self.font
        )

        self.ent_place = tk.Entry(
            self.frame_main,
            font=self.font,
            textvariable=self.place,
            bd=2
        )

        self.lbl_address = tk.Label(
            self.frame_main,
            text="Adresa:",
            font=self.font
        )

        self.ent_address = tk.Entry(
            self.frame_main,
            font=self.font,
            textvariable=self.address,
            bd=2
        )

        self.lbl_date = tk.Label(
            self.frame_main,
            font=self.font,
            text="Datum:"
        )

        self.calendar_date = DateEntry2(
            self.frame_main,
            font=self.font,
            locale="hr_HR",
            selectmode="day",
            state="readonly"
        )

        self.lbl_program = tk.Label(
            self.frame_main,
            text="Program:",
            font=self.font
        )

        self.cbx_program = CustomBox(
            self.frame_main,
            values=cbx_program_list,
            state="readonly",
            font=self.font,
        )

        self.lbl_hss_id = tk.Label(
            self.frame_main,
            text="hss_id:",
            font=self.font
        )

        self.validate_integer = (self.register(Tools.allow_only_integer))

        self.ent_hss_id = tk.Entry(
            self.frame_main,
            font=self.font,
            textvariable=self.hss_id,
            validate="all",
            validatecommand=(self.validate_integer, "%P"),
            bd=2
        )

        self.lbl_category = tk.Label(
            self.frame_main,
            text="Kategorija:",
            font=self.font,
        )

        self.chk_cadets = tk.Checkbutton(
            self.frame_main,
            font=self.font,
            text="kadeti",
            bg="red",
            variable=self.cadets,
            command=lambda: self.ColorCategories(self.chk_cadets)
        )

        self.chk_juniors = tk.Checkbutton(
            self.frame_main,
            font=self.font,
            text="juniori",
            bg="red",
            variable=self.juniors,
            command=lambda: self.ColorCategories(self.chk_juniors)
        )

        self.chk_seniors = tk.Checkbutton(
            self.frame_main,
            font=self.font,
            text="seniori",
            bg="red",
            variable=self.seniors,
            command=lambda: self.ColorCategories(self.chk_seniors)
        )

        self.chk_veterans = tk.Checkbutton(
            self.frame_main,
            font=self.font,
            text="veterani",
            bg="red",
            variable=self.veterans,
            command=lambda: self.ColorCategories(self.chk_veterans)
        )

        self.txt_additional = tk.Text(
            self.frame_note,
            font=self.font
        )

        self.btn_add = tk.Button(
            self.frame_buttons,
            text="Dodaj",
            bg="green",
            fg="black",
            font=self.font,
            command=lambda: self.Add()
        )
        self.grid_propagate(False)
        self.frame_note.pack_propagate(False)
        self.frame_buttons.grid_propagate(False)
        self.frame_main.grid_propagate(False)

        self.rowconfigure(0, weight=5, uniform="self_rows")
        self.rowconfigure(1, weight=2, uniform="self_rows")
        self.rowconfigure(2, weight=1, uniform="self_rows")
        self.columnconfigure(0, weight=1, uniform="self_cols")
        self.columnconfigure(1, weight=10, uniform="self_cols")
        self.columnconfigure(2, weight=1, uniform="self_cols")

        self.frame_main.grid(row=0, column=1, sticky="nsew")
        self.frame_note.grid(row=1, column=1, sticky="nsew")
        self.frame_buttons.grid(row=2, column=1, sticky="nsew")

        self.lbl_title.grid(row=1, column=0)
        self.ent_title.grid(row=1, column=1, columnspan=5, sticky="nsew")

        self.lbl_place.grid(row=3, column=0)
        self.ent_place.grid(row=3, column=1, columnspan=3, sticky="nsew")

        self.lbl_address.grid(row=5, column=0)
        self.ent_address.grid(row=5, column=1, columnspan=5, sticky="nsew")

        self.lbl_date.grid(row=7, column=0, sticky="nsew")
        self.calendar_date.grid(row=7, column=1, columnspan=2)

        self.lbl_program.grid(row=7, column=3, sticky="e")
        self.cbx_program.grid(row=7, column=4, columnspan=2, sticky="ew")

        self.lbl_hss_id.grid(row=9, column=0, sticky="nsew")
        self.ent_hss_id.grid(row=9, column=1, sticky="nsew")

        self.lbl_category.grid(row=11, column=0, columnspan=2)
        self.chk_cadets.grid(row=11, column=2, sticky="ew")
        self.chk_juniors.grid(row=11, column=3, sticky="ew")
        self.chk_seniors.grid(row=11, column=4, sticky="ew")
        self.chk_veterans.grid(row=11, column=5, sticky="ew")

        self.txt_additional.pack(expand=True, fill="both")

        self.btn_add.grid(row=1, rowspan=2, column=3, sticky="nsew")

        self.txt_additional.bind("<FocusIn>", self.ClearEmptyText)
        self.txt_additional.bind("<FocusOut>", self.InsertEmptyText)

        if self.modify:
            self.btn_add.configure(text="Uredi")

        self.values = {
            "hss_id": 0
        }
        if values is not None:
            self.values = values
            categories = Tools.TranslateCategoriesToList(self.values["Kategorija"])
            self.title.set(self.values["Naziv"])
            self.place.set(self.values["Mjesto"])
            self.address.set(self.values["Adresa"])
            self.cbx_program.set(self.values["Program"])
            self.hss_id.set(self.values['hss_id'])
            if "KAD" in categories:
                self.cadets.set(1)
            if "JUN" in categories:
                self.juniors.set(1)
            if "SEN" in categories:
                self.seniors.set(1)
            if "VET" in categories:
                self.veterans.set(1)
            self.txt_additional.delete("1.0", END)
            self.txt_additional.insert("1.0", self.values["Napomena"])
            self.calendar_date.set_date(Tools.SQL_date_format_to_croatian(self.values['Datum']))  # datetime.strptime(self.values["Datum"], "%Y-%m-%d").strftime("%d. %m. %Y."))
            self.ColorCategories(self.chk_cadets)
            self.ColorCategories(self.chk_juniors)
            self.ColorCategories(self.chk_seniors)
            self.ColorCategories(self.chk_veterans)

        self.InsertEmptyText(None)

    
    def ExitButton(self):
        self.values = None
        self.destroy()

    
    def ColorCategories(self, widget):
        value = int(widget.getvar(str(widget.cget("variable"))))
        if value:
            widget.configure(bg="green")
        else:
            widget.configure(bg="red")

    def Add(self):
        self.values["Naziv"] = self.title.get()
        self.values["Mjesto"] = self.place.get()
        self.values["Adresa"] = self.address.get()
        self.values["Datum"] = str(self.calendar_date.get_date())
        self.values["Program"] = self.cbx_program.get()
        self.values["Kategorija"] = Tools.TranslateCategoriesToInt(self.GetSelectedCategoryNames())
        self.values["Napomena"] = self.txt_additional.get("1.0", END)[:-1]  # remove \n at the end of text widget
        self.values["hss_id"] = self.hss_id.get()
        if self.save:
            if self.modify:
                DBUpdate.update_natjecanja_dict(self.values)
            else:
                self.values["id"] = DBAdder.add_competition_values(self.values)
        self.destroy()

    def ClearEmptyText(self, event):
        if self.txt_additional.get("1.0", END) == self.ent_empty_text + "\n":
            self.txt_additional.delete("1.0", END)  # delete all the text in the entry
            self.txt_additional.insert("1.0", '')  # Insert blank for user input
            self.txt_additional.configure(fg='black')

    
    def InsertEmptyText(self, event):
        if self.txt_additional.get("1.0", END) == '\n':
            self.txt_additional.insert("1.0", self.ent_empty_text)
            self.txt_additional.configure(fg="gray20")

    
    def GetSelectedCategoryNames(self):
        categories = []
        if self.cadets.get():
            categories.append("KAD")
        if self.juniors.get():
            categories.append("JUN")
        if self.seniors.get():
            categories.append("SEN")
        if self.veterans.get():
            categories.append("VET")
        return categories
