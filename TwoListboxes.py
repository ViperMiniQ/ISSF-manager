import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter.constants import END
from CustomListbox import RightClickMenuListbox
import HoverInfo


class TwoListboxes(tk.Frame):
    def __init__(self, parent, controller, font: tkFont.Font = None):
        tk.Frame.__init__(self, parent)

        self.last_selected_item_index_listbox_left = -1
        self.last_selected_item_index_listbox_right = -1

        self.font = font
        if not font:
            self.font = tkFont.Font(size=10)

        self.new_item_side = 0  # upon creation of a new item -> 0 defaults to left lbx, 1 to right lbx

        self.controller = controller
        self.notify_function = None

        self.lbx_left_items = {}
        self.lbx_right_items = {}
        self.items_descriptions = {}

        self.item_to_rename_from = None
        self.item_to_rename_to = {}
        self.renamed_item = {}  # key -> previous, value -> next

        self.frame_description = tk.Frame(self)

        self.columnconfigure(0, weight=5, uniform="frame_main_columns")
        self.columnconfigure(1, weight=2, uniform="frame_main_columns")
        self.columnconfigure(2, weight=5, uniform="frame_main_columns")

        self.rowconfigure(0, weight=1, uniform="frame_main_rows")
        self.rowconfigure(1, weight=3, uniform="frame_main_rows")
        self.grid_propagate(False)

        self.frame_lbx_left = tk.Frame(self, bg="red")
        self.frame_buttons = tk.Frame(self)
        self.frame_lbx_right = tk.Frame(self, bg="blue")

        for x in range(0, 10, 1):
            self.frame_buttons.rowconfigure(x, weight=1, uniform="main_buttons_rows")

        self.frame_buttons.columnconfigure(0, weight=1)

        self.lbx_left = RightClickMenuListbox(
            self.frame_lbx_left,
            selectmode=tk.SINGLE,
            font=self.font,
            bd=5
        )
        lbx_left_help_text = """Lista neaktivnih stavki"""
        self.lbx_left_help = HoverInfo.create_tooltip(
            widget=self.lbx_left,
            text=lbx_left_help_text,
            font_size=12,
            anchor="n",
            orientation="right"
        )

        self.lbx_right = RightClickMenuListbox(
            self.frame_lbx_right,
            selectmode=tk.SINGLE,
            font=self.font,
            bd=5
        )
        lbx_right_help_text = """Lista aktivnih stavki"""
        self.lbx_right_help = HoverInfo.create_tooltip(
            widget=self.lbx_right,
            text=lbx_right_help_text,
            font_size=12,
            anchor="n",
            orientation="left"
        )

        self.scr_lbx_left_vertical = tk.Scrollbar(
            self.frame_lbx_left,
            orient="vertical"
        )

        self.scr_lbx_left_horizontal = tk.Scrollbar(
            self.frame_lbx_left,
            orient="horizontal"
        )

        self.scr_lbx_right_vertical = tk.Scrollbar(
            self.frame_lbx_right,
            orient="vertical"
        )

        self.scr_lbx_right_horizontal = tk.Scrollbar(
            self.frame_lbx_right,
            orient="horizontal"
        )

        self.btn_add_left = tk.Button(
            self.frame_buttons,
            text=u"\u2190",
            font=self.font,
            bg="white",
            command=lambda: self.move_left()
        )
        btn_add_left_help_text = """Deaktiviranje stavki"""
        self.btn_add_left_help = HoverInfo.create_tooltip(
            widget=self.btn_add_left,
            text=btn_add_left_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_add_right = tk.Button(
            self.frame_buttons,
            text=u"\u2192",
            font=self.font,
            bg="white",
            command=lambda: self.move_right()
        )
        btn_add_right_help_text = """Aktiviranje stavki"""
        self.btn_add_right_help = HoverInfo.create_tooltip(
            widget=self.btn_add_right,
            text=btn_add_right_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_move_up = tk.Button(
            self.frame_buttons,
            text=u"\u2191",
            font=self.font,
            bg="white",
            command=lambda: self.move_up()
        )
        btn_move_up_help_text = """Pomicanje označene stavke više u poretku"""
        self.btn_move_up_help = HoverInfo.create_tooltip(
            widget=self.btn_move_up,
            text=btn_move_up_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_move_down = tk.Button(
            self.frame_buttons,
            text=u"\u2193",
            font=self.font,
            bg="white",
            command=lambda: self.move_down()
        )
        btn_move_down_help_text = """Pomicanje označene stavke dolje u poretku"""
        self.btn_move_down_help = HoverInfo.create_tooltip(
            widget=self.btn_move_down,
            text=btn_move_down_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_add_new = tk.Button(
            self.frame_buttons,
            text="+",
            font=self.font,
            bg="lime",
            command=lambda: self.add_new()
        )
        btn_add_new_help_text = """Kreiranje novih stavki"""
        self.btn_add_new_help = HoverInfo.create_tooltip(
            widget=self.btn_add_new,
            text=btn_add_new_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_rename = tk.Button(
            self.frame_buttons,
            text="Preimenuj",
            font=self.font,
            bg="deep sky blue",
            fg="black",
            command=lambda: self.rename_selected()
        )
        btn_rename_help_text = """Preimenovanje označene stavke. \nSvi unešeni podaci vezani uz stavku će se također osvježiti s novim nazivom stavke."""
        self.btn_add_new_help = HoverInfo.create_tooltip(
            widget=self.btn_rename,
            text=btn_rename_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.btn_delete = tk.Button(
            self.frame_buttons,
            text="Obriši",  # u"\ud83d\uddd1", #ne radi na Win7
            font=self.font,
            bg="black",
            fg="white",
            command=lambda: self.delete_selected()
        )
        btn_delete_help_text = """Brisanje označene stavke.\nUkoliko postoje unešeni podaci vezani uz stavku, osvježit će se s natpisom 'Nepoznato'.\nPreporuka je koristiti preimenovanje stavki umjesto brisanja i dodavanja zbog greške naziva ili opisa."""
        self.btn_delete_help = HoverInfo.create_tooltip(
            widget=self.btn_delete,
            text=btn_delete_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )

        self.lbl_description = tk.Label(
            self.frame_description,
            text="...",
            bd=10,
            font=self.font
        )
        self.lbl_description.pack(side="top", expand=True, fill="both")

        # listboxes menu

        # left lbx
        self.lbx_left_menu = tk.Menu(self, tearoff=0)
        self.lbx_left_menu.add_command(label="Dodaj", command=self.btn_add_new["command"])
        self.lbx_left_menu.add_separator()
        self.lbx_left_menu.add_command(label="Preimenuj", command=self.btn_rename["command"])
        self.lbx_left_menu.add_separator()
        self.lbx_left_menu.add_command(label="Pomakni gore", command=self.btn_move_up["command"])
        self.lbx_left_menu.add_command(label="Pomakni dolje", command=self.btn_move_down["command"])
        self.lbx_left_menu.add_separator()
        self.lbx_left_menu.add_command(label="Prebaci na desnu stranu", command=self.btn_add_right["command"])
        self.lbx_left_menu.add_separator()
        self.lbx_left_menu.add_command(label="Obriši", command=self.btn_delete["command"])
        self.lbx_left.assign_menu(self.lbx_left_menu)

        # right lbx
        self.lbx_right_menu = tk.Menu(self, tearoff=0)
        self.lbx_right_menu.add_command(label="Dodaj", command=self.btn_add_new["command"])
        self.lbx_right_menu.add_separator()
        self.lbx_right_menu.add_command(label="Preimenuj", command=self.btn_rename["command"])
        self.lbx_right_menu.add_separator()
        self.lbx_right_menu.add_command(label="Pomakni gore", command=self.btn_move_up["command"])
        self.lbx_right_menu.add_command(label="Pomakni dolje", command=self.btn_move_down["command"])
        self.lbx_right_menu.add_separator()
        self.lbx_right_menu.add_command(label="Prebaci na lijevu stranu", command=self.btn_add_left["command"])
        self.lbx_right_menu.add_separator()
        self.lbx_right_menu.add_command(label="Obriši", command=self.btn_delete["command"])
        self.lbx_right.assign_menu(self.lbx_right_menu)

        self.btn_add_left.grid(row=1, column=0, sticky="ew")
        self.btn_add_right.grid(row=2, column=0, sticky="ew")
        self.btn_move_up.grid(row=3, column=0, sticky="s")
        self.btn_move_down.grid(row=4, column=0, sticky="n")
        self.btn_add_new.grid(row=6, column=0, sticky="ew")
        self.btn_rename.grid(row=7, column=0, sticky="ew")
        self.btn_delete.grid(row=8, column=0, sticky="ew")

        self.lbx_right.configure(yscrollcommand=self.scr_lbx_right_vertical.set)
        self.lbx_right.configure(xscrollcommand=self.scr_lbx_right_horizontal.set)
        self.scr_lbx_right_vertical.configure(command=self.lbx_right.yview)
        self.scr_lbx_right_horizontal.configure(command=self.lbx_right.xview)
        self.lbx_left.configure(yscrollcommand=self.scr_lbx_left_vertical.set)
        self.lbx_left.configure(xscrollcommand=self.scr_lbx_left_horizontal.set)
        self.scr_lbx_left_vertical.configure(command=self.lbx_left.yview)
        self.scr_lbx_left_horizontal.configure(command=self.lbx_left.xview)

        self.lbx_left.bind("<Button-1>", lambda event: self.set_description(event, lbx="left"))
        self.lbx_right.bind("<Button-1>", lambda event: self.set_description(event, lbx="right"))

        self.frame_description.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.frame_lbx_left.grid(row=1, column=0, sticky="nsew")
        self.frame_buttons.grid(row=1, column=1, sticky="nsew")
        self.frame_lbx_right.grid(row=1, column=2, sticky="nsew")

        self.frame_lbx_left.columnconfigure(0, weight=1)
        self.frame_lbx_left.rowconfigure(0, weight=1)
        self.frame_lbx_right.rowconfigure(0, weight=1)
        self.frame_lbx_right.columnconfigure(0, weight=1)
        self.lbx_left.grid(row=0, column=0, sticky="nsew")
        self.lbx_right.grid(row=0, column=0, sticky="nsew")
        self.scr_lbx_right_vertical.grid(row=0, column=1, sticky="ns")
        self.scr_lbx_left_vertical.grid(row=0, column=1, sticky="ns")
        self.scr_lbx_left_horizontal.grid(row=1, column=0, sticky="ew")
        self.scr_lbx_right_horizontal.grid(row=1, column=0, stick="ew")

    def do_nothing(self):
        pass

    def set_fullcontrol(self):
        """Alows moving items between two listboxes and chaninng items positions in listbox \n
        New item can be added and existing items can be deleted"""
        self.btn_delete.configure(command=lambda: self.delete_selected(), bg="black")
        self.btn_add_new.configure(command=lambda: self.add_new(), bg="lime")
        self.btn_move_up.configure(command=lambda: self.move_up(), bg="white")
        self.btn_move_down.configure(command=lambda: self.move_down(), bg="white")
        self.btn_add_left.configure(command=lambda: self.move_left(), bg="white")
        self.btn_add_right.configure(command=lambda: self.move_right(), bg="white")
        self.btn_rename.configure(command=lambda: self.rename_selected(), bg="yellow")

    def set_manipulateonly(self):
        """Allows moving items between two listboxes and changing items positions in listbox \n
        New items can't be added, existing items can't be deleted"""
        self.btn_delete.configure(command=self.do_nothing, bg="red")
        self.btn_add_new.configure(command=self.do_nothing, bg="red")
        self.btn_move_up.configure(command=lambda: self.move_up(), bg="white")
        self.btn_move_down.configure(command=lambda: self.move_down(), bg="white")
        self.btn_add_left.configure(command=lambda: self.move_left(), bg="white")
        self.btn_add_right.configure(command=lambda: self.move_right(), bg="white")
        self.btn_rename.configure(command=self.do_nothing, bg="red")

    def set_readonly(self):
        """No manipulation of items in listboxes is possible. \n
        New items can't be added, existing items can't be deleted"""
        self.btn_delete.configure(command=self.do_nothing, bg="red")
        self.btn_add_new.configure(command=self.do_nothing, bg="red")
        self.btn_move_up.configure(command=self.do_nothing, bg="red")
        self.btn_move_down.configure(command=self.do_nothing, bg="red")
        self.btn_add_left.configure(command=self.do_nothing, bg="red")
        self.btn_add_right.configure(command=self.do_nothing, bg="red")

    def set_state(self, state: str):
        """Implementation missing"""
        if state == "readonly":
            self.set_readonly()

    def clear_listbox(self, listbox: str):
        """listbox: 'right' or 'left'"""
        if listbox == "right":
            self.lbx_right.delete(0, tk.END)
        elif listbox == "left":
            self.lbx_left.delete(0, tk.END)

    def set_notify_function(self, function):
        self.notify_function = function

    def notify(self):
        try:
            self.notify_function()
        except:
            pass

    def ask_deletion_confirmation(self, item_to_delete_name: str):
        ask = messagebox.askyesno(title="Brisanje stavke",
                                  message=f"Jeste li sigurni da želite ukloniti {item_to_delete_name}?"
            )
        return ask

    def rename_selected(self):
        curselection = None
        selected_lbx = None
        selected_side_items = None
        if self.lbx_right.curselection():
            curselection = self.lbx_right.curselection()
            selected_lbx = self.lbx_right
            selected_side_items = self.lbx_right_items
        elif self.lbx_left.curselection():
            curselection = self.lbx_left.curselection()
            selected_lbx = self.lbx_left
            selected_side_items = self.lbx_left_items
        if curselection is None:
            return
        name = selected_lbx.get(curselection)
        description = self.items_descriptions[name]
        new_item = RenameItem(self, name, description)
        new_item.wait_window()
        if new_item.dictionary:
            self.item_to_rename_from = name
            item_to_rename_to_name = new_item.dictionary["name"]
            item_to_rename_from_description = new_item.dictionary["description"]
            self.item_to_rename_to[item_to_rename_to_name] = item_to_rename_from_description
            renamed_item_index = selected_lbx.get(0, tk.END).index(self.item_to_rename_from)
            selected_lbx.delete(renamed_item_index)
            selected_lbx.insert(renamed_item_index, new_item.dictionary["name"])
            self.items_descriptions.pop(self.item_to_rename_from)
            self.items_descriptions[item_to_rename_to_name] = item_to_rename_from_description
            selected_side_items.pop(self.item_to_rename_from)
            selected_side_items[item_to_rename_to_name] = renamed_item_index
            self.notify()
        self.item_to_rename_from = None
        self.item_to_rename_to = {}

    def delete_selected(self):
        curselection = None
        selected_lbx = None
        selected_lbx_items = None
        side = "right"
        if self.lbx_right.curselection():
            curselection = self.lbx_right.curselection()
            selected_lbx = self.lbx_right
            selected_lbx_items = self.lbx_right_items
        elif self.lbx_left.curselection():
            curselection = self.lbx_left.curselection()
            selected_lbx = self.lbx_left
            selected_lbx_items = self.lbx_left_items
            side = "left"
        if curselection is None:
            return
        item_to_delete = selected_lbx.get(curselection)
        if self.ask_deletion_confirmation(item_to_delete):
            selected_lbx.delete(curselection)
            selected_lbx_items.pop(item_to_delete)
            self.items_descriptions.pop(item_to_delete)
            self.refresh_listbox_elements(side)
            self.notify()

    def add_new(self):
        new_item = NewItem(self)
        new_item.wait_window()
        if new_item.dictionary:
            if not self.new_item_side:
                self.lbx_left_items[new_item.dictionary["name"]] = 0
                self.items_descriptions[new_item.dictionary["name"]] = new_item.dictionary["description"]
                self.refresh_listbox_elements("left")
            else:
                self.lbx_right_items[new_item.dictionary["name"]] = len(self.lbx_right_items) + 1
                self.items_descriptions[new_item.dictionary["name"]] = new_item.dictionary["description"]
                self.refresh_listbox_elements("right")
            self.notify()

    def refresh_listbox_elements(self, listbox: str):
        """listbox: 'active' or 'inactive'"""
        self.clear_listbox(listbox)
        if listbox == "right":
            for key, value in self.lbx_right_items.items():
                self.lbx_right.insert(tk.END, key)
        elif listbox == "left":
            for key, value in self.lbx_left_items.items():
                self.lbx_left.insert(tk.END, key)

    def set_left_listbox_dict(self, values_with_positions):
        self.lbx_left_items = values_with_positions

    def set_right_listbox_dict(self, values_with_positions):
        self.lbx_right_items = values_with_positions

    def update_listbox_descriptions(self, values_with_descriptions):
        self.items_descriptions = values_with_descriptions

    def update_left_listbox_values(self, values_with_positions: dict):
        self.lbx_left_items = values_with_positions
        self.refresh_listbox_elements("left")

    def update_right_listbox_values(self, values_with_positions: dict):
        self.lbx_right_items = values_with_positions
        self.refresh_listbox_elements("right")

    def set_font_size(self, size: int):
        self.font.configure(size=size)

    def set_description(self, event, lbx):
        try:
            if lbx == "left":
                if self.lbx_left.curselection():
                    self.lbl_description["text"] = self.items_descriptions[self.lbx_left.get(self.lbx_left.curselection())]
            elif lbx == "right":
                if self.lbx_right.curselection():
                    self.lbl_description["text"] = self.items_descriptions[self.lbx_right.get(self.lbx_right.curselection())]
        except KeyError:
            pass

    def move_right(self):
        if self.lbx_left.curselection():
            # change item sides in listboxes
            selected_item_index = self.lbx_left.curselection()
            selected_item = self.lbx_left.get(selected_item_index)
            self.lbx_left.delete(selected_item_index)
            self.lbx_right.insert(tk.END, selected_item)

            # update dictionaries
            last_position_in_right_lbx = len(self.lbx_right_items)
            self.lbx_right_items[selected_item] = last_position_in_right_lbx + 1
            self.lbx_left_items.pop(selected_item)
            self.notify()

    def move_left(self):
        if self.lbx_right.curselection():
            # change item sides in listboxes
            selected_item_index = self.lbx_right.curselection()
            selected_item = self.lbx_right.get(selected_item_index)
            self.lbx_right.delete(selected_item_index)
            self.lbx_left.insert(tk.END, selected_item)

            # update dictionaries
            last_position_in_left_lbx = len(self.lbx_left_items)
            self.lbx_left_items[selected_item] = last_position_in_left_lbx + 1
            self.lbx_right_items.pop(selected_item)

            self.notify()

    def move_up(self, *args):
        try:
            lbx_pos = self.lbx_right.curselection()
            if not lbx_pos:
                return
            for pos in lbx_pos:
                if pos == 0:
                    continue
                text = self.lbx_right.get(pos)
                above = self.lbx_right.get(pos - 1)

                temp = self.lbx_right_items[text]
                self.lbx_right_items[text] = self.lbx_right_items[above]
                self.lbx_right_items[above] = temp

                self.lbx_right.delete(pos)
                self.lbx_right.insert(pos - 1, text)
            self.lbx_right.select_set(pos - 1)
            self.last_selected_item_index_listbox_right = self.lbx_right.curselection()[0]
            self.notify()
        except:
            pass

    def move_down(self, *args):
        try:
            lbx_pos = self.lbx_right.curselection()
            if not lbx_pos:
                return
            for pos in lbx_pos:
                # Are we at the bottom of the list?
                if pos == self.lbx_right.size() - 1:
                    continue
                text = self.lbx_right.get(pos)
                below = self.lbx_right.get(pos + 1)

                temp = self.lbx_right_items[text]
                self.lbx_right_items[text] = self.lbx_right_items[below]
                self.lbx_right_items[below] = temp

                self.lbx_right.delete(pos)
                self.lbx_right.insert(pos + 1, text)
            self.lbx_right.selection_set(pos + 1)
            self.last_selected_item_index_listbox_right = self.lbx_right.curselection()[0]
            self.notify()
        except:
            pass

    def select_item(self, listbox: str, index: int):
        """listbox: 'right' or 'left'"""
        if listbox == "right":
            self.lbx_right.selection_set(index)
            return
        if listbox == "left":
            self.lbx_left.selection_set(index)
            return

    def SetFont(self, size: int):
        self.font.configure(size=size)


class RenameItem(tk.Toplevel):
    def __init__(self, parent, name: str, description: str):
        tk.Toplevel.__init__(self, parent)
        self.dictionary = {}

        self.font_14 = tkFont.Font(size=14)

        self.frame_from = tk.Frame(self)
        self.frame_from.columnconfigure(0, weight=1, uniform="col")
        self.frame_from.columnconfigure(1, weight=4, uniform="col")
        self.frame_from.rowconfigure(0, weight=1, uniform="row")
        self.frame_from.rowconfigure(1, weight=7, uniform="row")

        self.frame_to = tk.Frame(self)
        self.frame_to.columnconfigure(0, weight=1, uniform="col")
        self.frame_to.columnconfigure(1, weight=4, uniform="col")
        self.frame_to.rowconfigure(0, weight=1, uniform="row")
        self.frame_to.rowconfigure(1, weight=7, uniform="row")

        self.lbl_from = tk.Label(
            self.frame_from,
            font=self.font_14,
            text="IZ:"
        )

        self.lbl_to = tk.Label(
            self.frame_to,
            font=self.font_14,
            text="U:"
        )

        x = 600
        y = 200

        self.geometry("{}x{}".format(x, y))

        self.item_from = BasicNameDescriptionItem(self.frame_from, name=name, description=description)
        self.item_from.ent_short.configure(state="disabled")
        self.item_from.txt_description.configure(state="disabled")
        self.item_to = BasicNameDescriptionItem(self.frame_to, name="", description="")

        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        self.rowconfigure(0, weight=10, uniform="row")
        self.rowconfigure(0, weight=1, uniform="row")

        self.lbl_from.grid(row=0, column=0, sticky="nsew")
        self.lbl_to.grid(row=0, column=0, sticky="nsew")
        self.item_from.grid(row=1, column=0, columnspan=2)
        self.item_to.grid(row=1, column=0, columnspan=2)

        self.btn_rename = tk.Button(
            self,
            text="Potvrdi",
            bg="yellow",
            fg="black",
            font=self.font_14,
            command=self.save_and_exit
        )

        self.btn_rename.grid(row=1, column=0, columnspan=2)

        self.frame_from.grid(row=0, column=0, sticky="nsew")
        self.frame_to.grid(row=0, column=1, sticky="nsew")

    def save_and_exit(self):
        if self.item_to.get_name() and self.item_to.get_name() != self.item_from.get_name():
            self.dictionary["name"] = self.item_to.get_name()
            self.dictionary["description"] = self.item_to.get_description()
        self.destroy()


class NewItem2(tk.Toplevel):
    def __init__(self, parent, name: str = "", description: str = ""):
        tk.Toplevel.__init__(self, parent)
        self.dictionary = {}

        self.ent_empty_text = "Opis..."

        self.font = tkFont.Font(size=14)

        self.columnconfigure(0, weight=1, uniform="columns")
        self.columnconfigure(1, weight=10, uniform="columns")
        self.columnconfigure(2, weight=1, uniform="columns")

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=5, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=10, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")
        self.rowconfigure(5, weight=5, uniform="rows")
        self.rowconfigure(6, weight=1, uniform="rows")

        x = 300
        y = 100

        self.geometry("{}x{}".format(x, y))

        self.ent_short = tk.Entry(
            self,
            width=10,
            font=self.font
        )

        self.txt_description = tk.Text(
            self,
            width=80,
            height=2,
            font=self.font
        )

        self.btn_confirm = tk.Button(
            self,
            text="Dodaj",
            command=lambda: self.save_and_exit()
        )

        self.txt_description.insert("1.0", description)
        self.ent_short.insert(0, name)

        self.ent_short.grid(row=1, column=1, sticky="nsew")
        self.txt_description.grid(row=3, column=1, sticky="nsew")
        self.btn_confirm.grid(row=5, column=1, sticky="nsew")

        self.txt_description.bind("<FocusIn>", self.clear_empty_text)
        self.txt_description.bind("<FocusOut>", self.insert_empty_text)

        self.insert_empty_text(None)

    def save_and_exit(self):
        dictionary = {}
        if self.ent_short.get() and self.txt_description.get("1.0", END):
            dictionary["name"] = self.ent_short.get()
            dictionary["description"] = self.txt_description.get("1.0", END)
            self.dictionary = dictionary
            self.destroy()

    def clear_empty_text(self, event):
        if self.txt_description.get("1.0", END) == self.ent_empty_text + "\n":
            self.txt_description.delete("1.0", END)  # delete all the text in the entry
            self.txt_description.insert("1.0", '')  # Insert blank for user input
            self.txt_description.configure(fg='black')

    def insert_empty_text(self, event):
        if self.txt_description.get("1.0", END) == '\n':
            self.txt_description.insert("1.0", self.ent_empty_text)
            self.txt_description.configure(fg="gray20")


class NewItem(tk.Toplevel):
    def __init__(self, parent, name: str = "", description: str = ""):
        tk.Toplevel.__init__(self, parent)
        self.dictionary = {}

        self.geometry("{}x{}".format(300, 150))

        self.rowconfigure(0, weight=3, uniform="row")
        self.rowconfigure(1, weight=1, uniform="row")

        self.columnconfigure(0, weight=4, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        self.grid_propagate(False)

        self.frame_main = BasicNameDescriptionItem(self, name, description)
        self.btn_confirm = tk.Button(
            self,
            text="Dodaj",
            bg="lime",
            fg="black",
            command=self.btn_confirm_click
        )

        self.frame_main.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.btn_confirm.grid(row=1, column=1, sticky="nsew")

    def btn_confirm_click(self):
        if self.frame_main.get_name():
            self.dictionary["name"] = self.frame_main.get_name()
            self.dictionary["description"] = self.frame_main.get_description()
        self.destroy()


class BasicNameDescriptionItem(tk.Frame):
    def __init__(self, parent, name, description):
        tk.Frame.__init__(self, parent)
        self.ent_empty_text = "Opis..."

        self.font = tkFont.Font(size=14)

        self.columnconfigure(0, weight=1, uniform="columns")
        self.columnconfigure(1, weight=10, uniform="columns")
        self.columnconfigure(2, weight=1, uniform="columns")

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=5, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=10, uniform="rows")
        #self.rowconfigure(4, weight=1, uniform="rows")
        #self.rowconfigure(5, weight=5, uniform="rows")
        #self.rowconfigure(6, weight=1, uniform="rows")

        self.ent_short = tk.Entry(
            self,
            width=10,
            font=self.font
        )

        self.txt_description = tk.Text(
            self,
            width=80,
            height=2,
            font=self.font
        )

        self.txt_description.insert("1.0", description)
        self.ent_short.insert(0, name)

        self.ent_short.grid(row=1, column=1, sticky="nsew")
        self.txt_description.grid(row=3, column=1, sticky="nsew")

        self.txt_description.bind("<FocusIn>", self.clear_empty_text)
        self.txt_description.bind("<FocusOut>", self.insert_empty_text)

        self.insert_empty_text(None)

    def get_name(self):
        return self.ent_short.get()

    def get_description(self):
        return self.txt_description.get("1.0", tk.END)

    def clear_empty_text(self, event):
        if self.txt_description.get("1.0", END) == self.ent_empty_text + "\n":
            self.txt_description.delete("1.0", END)  # delete all the text in the entry
            self.txt_description.insert("1.0", '')  # Insert blank for user input
            self.txt_description.configure(fg='black')

    def insert_empty_text(self, event):
        if self.txt_description.get("1.0", END) == '\n':
            self.txt_description.insert("1.0", self.ent_empty_text)
            self.txt_description.configure(fg="gray20")