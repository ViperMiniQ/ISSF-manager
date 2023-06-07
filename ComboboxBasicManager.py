import tkinter as tk
import tkinter.font as tkFont
from CustomListbox import RightClickMenuListbox
from CustomWidgets import CustomBox


class ItemBasicManager(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.controller = parent
        self.notif_func = None

        self.lbx_font = tkFont.Font(size=10)
        self.cbx_font = tkFont.Font(size=20)

        self.items = {}
        self.lbx_items = []
        self.lbx_frame = tk.Frame(self)

        # <GRID> #
        self.rowconfigure(0, weight=1, uniform="shooters_rows")
        self.rowconfigure(1, weight=5, uniform="shooters_rows")
        self.rowconfigure(2, weight=1, uniform="shooters_rows")
        self.columnconfigure(0, weight=1, uniform="shooters_columns")
        self.columnconfigure(1, weight=1, uniform="shooters_columns")
        self.columnconfigure(2, weight=1, uniform="shooters_columns")
        # </GRID> #

        self.cbx = CustomBox(
            self,
            justify="center",
            font=self.cbx_font,
            state="readonly"
        )

        self.lbx = RightClickMenuListbox(
            self.lbx_frame,
            selectmode=tk.SINGLE,
            justify="center",
            font=self.lbx_font
        )

        self.scr_lbx = tk.Scrollbar(
            self.lbx_frame,
            orient="vertical"
        )

        self.lbx.configure(yscrollcommand=self.scr_lbx.set)
        self.scr_lbx.configure(command=self.lbx.yview)

        self.btn_add = tk.Button(
            self,
            text="Dodaj",
            font=self.lbx_font,
            bg="green",
            command=lambda: self._add_new()
        )

        self.btn_show_info = tk.Button(
            self,
            text="Prikaži",
            font=self.lbx_font,
            bg="yellow",
            command=lambda: self.notify()
        )

        self.btn_delete = tk.Button(
            self,
            text="Obriši",
            font=self.lbx_font,
            bg="red",
            command=lambda: self._delete_selected()
        )

        self.lbx_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.scr_lbx.pack(side="right", fill="y")
        self.lbx.pack(side="left", expand=True, fill="both")

        self.cbx.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.btn_add.grid(row=2, column=0, sticky="nsew")

        self.btn_show_info.grid(row=2, column=1, sticky="nsew")
        self.btn_delete.grid(row=2, column=2, sticky="nsew")

        self.lbx.bind("<Double-Button-1>", self.notify)
        self.cbx.bind("<<ComboboxSelected>>", self._update_values)

    def set_button_font(self, font: tkFont.Font):
        self.btn_add.configure(font=font)
        self.btn_delete.configure(font=font)
        self.btn_show_info.configure(font=font)

    def set_listbox_font(self, font: tkFont.Font):
        self.lbx.configure(font=font)

    def set_combobox_entry_font(self, font: tkFont.Font):
        self.cbx.configure(font=font)

    def set_notify_function(self, func):
        self.notif_func = func

    def _append_to_lbx(self, item: str):
        self.lbx.insert(tk.END, item)

    def _refresh_cbx_values(self, values: list):
        self.cbx.configure(values=values)
        if values:
            self.cbx.current(0)

    def _clear_lbx(self):
        self.lbx.delete(0, tk.END)

    def _update_values(self, event=None):
        pass

    def _recreate_lbx_scrollbar(self):
        self.scr_lbx.destroy()
        self.lbx.destroy()

        self.lbx = tk.Listbox(
            self.lbx,
            selectmode=tk.SINGLE,
            justify="center",
            font=self.lbx_font
        )

        self.scr_lbx = tk.Scrollbar(
            self.lbx,
            orient="vertical"
        )

        self.scr_lbx.configure(command=self.lbx.yview)
        self.lbx.configure(yscrollcommand=self.scr_lbx.set)

        self.scr_lbx.pack(side="right", fill="y")
        self.lbx.pack(side="right", fill="both", expand=True)

        self.lbx.bind("<Double-Button-1>", self.notify)

        self._update_values()

    def get_selected_item_id(self):
        """Returns -1 if nothing is selected, otherwise, returns dictionary value of the selected item"""
        if self.lbx.curselection():
            return self.items[self.lbx.get(self.lbx.curselection())]
        return -1

    def get_item_in_focus(self):
        return self.lbx.get(self.lbx.curselection())
    
    def notify(self, event=None):
        if self.notif_func is not None:
            self.notif_func()

    def _add_new(self):
        pass

    def _delete_selected(self):
        pass
    
    def _show_selected(self):
        pass
