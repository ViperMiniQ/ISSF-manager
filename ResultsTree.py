import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from datetime import datetime
import CheckbuttonFrame
from collections import Counter

# https://www.geeksforgeeks.org/hierarchical-treeview-in-python-gui-application/

import Tools
import Colors


class ResultsTree(tk.Frame):
    def __init__(self, parent, controller, columns_dict, column_widths_dict, column_types_dict, style: str, font):
        """Dictionary values must be under the same key"""
        tk.Frame.__init__(self, parent)
        self.str_style = style
        self.controller = controller
        self.tree_even_row = False
        self.treeview_columns_dict = columns_dict
        self.treeview_column_widths = column_widths_dict
        self.treeview_column_types = column_types_dict
        self.style = ttk.Style()
        self.treeview_style = ttk.Style()
        self.treeview_style.configure(self.str_style + ".Treeview")

        self.style.configure(self.str_style + ".Treeview.Heading", font=(None, 20), rowheight=20)

        if isinstance(font, tkFont.Font):
            self.tree_item_font = font
        else:
            self.tree_item_font = tkFont.Font(size=14)

        columns = self.GetColumnsToDisplay(self.treeview_columns_dict)
        self.tree_shooter = ttk.Treeview(
            self,
            columns=[str(column) for column in self.treeview_columns_dict],
            show="headings",
            style=self.str_style + ".Treeview",
            displaycolumns=columns
        )

        self.scr_tree_shooter_vertical = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree_shooter.yview
        )
        self.tree_shooter.configure(yscrollcommand=self.scr_tree_shooter_vertical.set)

        self.scr_tree_shooter_horizontal = tk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree_shooter.xview
        )
        self.tree_shooter.configure(xscrollcommand=self.scr_tree_shooter_horizontal.set)

        for key, value in self.treeview_column_types.items():
            self.tree_shooter.heading(key, text=key, anchor="center", command=lambda col=key, col_type=value: self.treeview_sort_column(self.tree_shooter, col, col_type, False))
        for column in self.tree_shooter["columns"]:
            self.tree_shooter.column(column, anchor="center", stretch=True)

        self.scr_tree_shooter_horizontal.pack(side="bottom", fill="x")
        self.tree_shooter.pack(side="left", expand=True, fill="both")
        self.scr_tree_shooter_vertical.pack(side="right", fill="y")

        self.tree_shooter.bind("i", self.BindI)
        self.tree_shooter.bind("I", self.BindI)
        self.tree_shooter.tag_configure("font", font=self.tree_item_font)

        self.tree_shooter.bind("<Shift-3>", self.double_click_heading)

        self.menu = None

        Colors.subscribe(self)
        self.load_colors()

    def assign_menu(self, menu):
        self.menu = menu
        self.tree_shooter.bind("<Button-3>", self.right_click_menu)

    def right_click_menu(self, event):
        rowID = self.tree_shooter.identify_row(event.y)
        self.tree_shooter.focus(rowID)
        self.tree_shooter.selection_set(rowID)
        menu_y = event.y_root - self.menu.winfo_reqheight()
        if menu_y < 0:
            menu_y = event.y_root
        if self.menu and rowID:
            try:
                self.menu.tk_popup(event.x_root, menu_y)
            finally:
                self.menu.grab_release()

    def double_click_heading(self, event):
        column = self.tree_shooter.identify_column(event.x)
        self.adjust_column_size(column, self.tree_item_font.measure(self.get_max_string_in_column(column)) + 10)

    def adjust_all_columns_default(self):
        for column in self.tree_shooter["displaycolumns"]:
            self.adjust_column_size(column, int(self.treeview_column_widths[column]))
        self.tree_shooter.update()
    
    def adjust_all_columns_by_text_length(self):
        total_columns_size = 0
        adjust_size = 0
        tree_column_sizes = {}
        for column in self.tree_shooter["displaycolumns"]:
            longest_string_in_column_size = self.tree_item_font.measure(
                self.get_max_string_in_column(column),
                displayof=self.tree_shooter
            )
            tree_column_sizes[column] = longest_string_in_column_size
            total_columns_size += longest_string_in_column_size
        self.tree_shooter.update_idletasks()

        if total_columns_size < self.tree_shooter.winfo_width():
            adjust_size = self.tree_shooter.winfo_width() - total_columns_size
            adjust_size /= len(self.tree_shooter["displaycolumns"])
        if adjust_size < 10:
            adjust_size = 10
        for column in self.tree_shooter["displaycolumns"]:
            self.adjust_column_size(column, int(tree_column_sizes[column] + adjust_size))
        self.tree_shooter.update()

    def TreeviewReturn(self):
        pass

    def GetColumnsToDisplay(self, dictionary):
        """Returns list of columns to display"""
        columns = []
        for key, value in dictionary.items():
            if value:
                columns.append(key)
        return columns

    def set_colors(self, odd_row_bg: str, even_row_bg: str, odd_row_fg: str, even_row_fg: str):
        self.tree_shooter.tag_configure(
            "odd_row",
            background=odd_row_bg
        )
        self.tree_shooter.tag_configure(
            "even_row",
            background=even_row_bg
        )
        self.tree_shooter.tag_configure(
            "odd_row",
            foreground=odd_row_fg
        )
        self.tree_shooter.tag_configure(
            "even_row",
            foreground=even_row_fg
        )

    def load_colors(self):
        self.tree_shooter.tag_configure(
            "odd_row",
            background=Colors.colors["Results"]["treeview"]["odd_rows"]["bg"]
        )
        self.tree_shooter.tag_configure(
            "even_row",
            background=Colors.colors["Results"]["treeview"]["even_rows"]["bg"]
        )
        self.tree_shooter.tag_configure(
            "odd_row",
            foreground=Colors.colors["Results"]["treeview"]["odd_rows"]["fg"]
        )
        self.tree_shooter.tag_configure(
            "even_row",
            foreground=Colors.colors["Results"]["treeview"]["even_rows"]["fg"]
        )

    def change_odd_rows_bg_color(self, color: str):
        self.tree_shooter.tag_configure("odd_row", background=color)

    def change_even_rows_bg_color(self, color: str):
        self.tree_shooter.tag_configure("even_row", background=color)

    def change_odd_rows_text_color(self, color: str):
        self.tree_shooter.tag_configure("odd_row", foreground=color)

    def change_even_rows_text_color(self, color: str):
        self.tree_shooter.tag_configure("even_row", foreground=color)
    
    def ChangeTreeviewEvenRowsColor(self, color):
        """color -> string"""
        self.tree_shooter.tag_configure("even_row", background=color)

    def ChangeTreeviewOddRowsColor(self, color):
        """color -> string"""
        self.tree_shooter.tag_configure("odd_row", background=color)

    def DeleteTreeRow(self, row):
        """if row="current", delete currently selected row"""
        if row == "selected":
            self.tree_shooter.delete(self.tree_shooter.selection()[0])

    def ClearTree(self):
        self.tree_shooter.delete(*self.tree_shooter.get_children())

    def adjust_column_size(self, column, size: int):
        self.tree_shooter.column(column, minwidth=size, width=size, stretch=False)

    def GetNumberOfTreeviewColumns(self):
        return len(self.treeview_columns_dict)

    def GetNumberOfItemsInTreeview(self):
        return len(self.tree_shooter.get_children())

    def AddRowToTree(self, values, top=False):
        """Adds row to treeview, top=False adds it at the bottom, top=True at the top"""
        pass

    def update_selected_row(self, values: dict):
        selection = self.tree_shooter.focus()

        if not selection:
            return 0

        for key in self.treeview_columns_dict.keys():
            try:
                self.tree_shooter.set(
                    item=selection,
                    column=key,
                    value=values[key]
                )
            except:
                pass

    def get_values_of_selected_row(self):
        """Returns dictionary of column: value for selected row"""
        selection = self.tree_shooter.focus()
        if not selection:
            return 0
        return_values = self.tree_shooter.set(selection)
        return_values["rowID"] = selection
        return return_values

    def EditTreeviewRowValues(self, row_id, tree_row_values):
        for key, value in self.treeview_columns_dict.items():
            self.tree_shooter.set(row_id, column=key, value=tree_row_values[key])

    
    def ListifyTreeRowValues(self, values_dict):
        values_list = []
        for key, value in self.treeview_columns_dict.items():
            values_list.append(values_dict[key])

        return values_list

    def _get_list_from_dictionary_for_insertion(self, dict_):
        prepared_list = []
        for key in self.treeview_columns_dict.keys():
            prepared_list.append(str(dict_[key]))
        return prepared_list


    def AddResultToTree(self, tree_row_values_dict, top=False):
        """tree_values -> dictionary
        top=False add new record at the end, top=True at the top"""
        tree_row_values = self._get_list_from_dictionary_for_insertion(tree_row_values_dict)

        if self.GetNumberOfItemsInTreeview() % 2 == 0:
            row = "even_row"
        else:
            row = "odd_row"

        if not top:
            self.tree_shooter.insert("", tk.END, values=tree_row_values, tags=("font", row))
        else:
            self.tree_shooter.insert("", 0, values=tree_row_values, tags=("font", row))

        #self.refresh_columns_summary()

    
    def refresh_columns_summary(self):
        for column in self.tree_shooter["columns"]:
            column_occurrences = self.get_occurrences_in_column(column)
            top_5_occurrences = self.get_top_5_occurrences(column_occurrences)

    
    def set_treeview_items_font(self, size: int, family: str =None):
        self.tree_item_font.configure(size=size, family=family)

    
    def set_treeview_heading_font(self, size: int, family: str =None):
        self.style.configure(self.str_style + ".Treeview.Heading", font=(family, size))

    
    def set_treeview_heading_height(self, height: int):
        self.style.configure(self.str_style + ".Treeview.Heading", rowheight=height)

    
    def set_treeview_items_height(self, height: int):
        self.style.configure(self.str_style + ".Treeview", rowheight=height)

    
    def IncreaseTreeItemFontSize(self):
        if self.tree_item_font["size"] < 72:
            font_size = self.tree_item_font["size"] + 1
            self.set_treeview_items_font(font_size)  #self.tree_item_font["size"] = font_size
            self.set_treeview_heading_height(font_size)
            self.set_treeview_heading_font(font_size) #self.style.configure("Treeview.Heading", font=(None, font_size), rowheight=font_size)
            self.set_treeview_items_height(int(font_size * 1.75)) #self.treeview_style.configure("T.Treeview", rowheight=int(font_size * 1.7))

    
    def DecreaseTreeItemFontSize(self):
        if self.tree_item_font["size"] > 4:
            font_size = self.tree_item_font["size"] - 1
            self.set_treeview_items_font(font_size)  # self.tree_item_font["size"] = font_size
            self.set_treeview_heading_height(font_size)
            self.set_treeview_heading_font(font_size)  # self.style.configure("Treeview.Heading", font=(None, font_size), rowheight=font_size)
            self.set_treeview_items_height(int(font_size * 1.75))

    
    def BindI(self, event=None):
        self.controller.BindI()

    
    def SetColumnWidth(self, dict, values):
        self.update_idletasks()
        x = self.winfo_width() - 17
        if not x:
            x = 800 - 17
        values_sum = 0
        for i, key in enumerate(dict):
            if dict[key]:
                values_sum += values[key]

        multiplier = x / values_sum
        for i, key in enumerate(dict):
            if dict[key]:
                self.tree_shooter.column(key, stretch=True, width=int(values[key]*multiplier), anchor="center")
        self.scr_tree_shooter_horizontal.pack(side="bottom", fill="x")
        self.scr_tree_shooter_vertical.pack(side="right", fill="y")

    
    def SelectColumnsToDisplay(self):
        columns_dict = SelectColumnsToDisplay(self, self.treeview_columns_dict)
        columns_dict.wait_window()
        if columns_dict.values:
            columns = self.GetColumnsToDisplay(columns_dict.values)
            self.treeview_columns_dict = columns_dict.values
            self.tree_shooter.configure(displaycolumns=columns)

    
    def treeview_sort_column(self, tv, col, col_type, reverse):
        self.hastag = False
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        if col_type == "date":
            l.sort(key=lambda x: datetime.strptime(x[0], "%d. %m. %Y."),
                   reverse=reverse)  # x is a list of tuples containing values in column and their position in column (ex: [('05.01.2021.', 'I001'), ('05.01.2021.', 'I002'), ('07.01.2021.', 'I003')...]
        elif col_type == "int":
            l.sort(key=lambda x: int(x[0].strip() or 0), reverse=reverse)
        elif col_type == "float":
            l.sort(key=lambda x: float(x[0].strip() or 0), reverse=reverse)
        elif col_type == "str":
            l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        even_row = True
        for index, (val, k) in enumerate(l):
            if even_row:
                row = "even_row"
            else:
                row = "odd_row"
            even_row = not even_row
            tv.move(k, '', index)
            self.tree_shooter.item(k, tags=("font", row))

        # reverse sort next time
        tv.heading(col, command=lambda _col=col, _col_type=col_type: self.treeview_sort_column(tv, _col, _col_type, not reverse))

    def get_max_string_in_column(self, column):
        tuples = self.get_values_in_column(column)
        values = [value[0] for value in tuples]
        return Tools.longest_string_in_list(values)

    def get_occurrences_in_column(self, column):
        """returns Counter(item, count)"""
        return Counter(tup[0] for tup in self.get_values_in_column(column))

    def get_top_5_occurrences(self, dictionary: Counter):
        """returns Counter(item, count)"""
        return dictionary.most_common(5)

    def get_values_in_column(self, column):
        """Returns list of tuples (value, item)"""
        return [(self.tree_shooter.set(k, column), k) for k in self.tree_shooter.get_children('')]

    def keep_aspect_ratio(self):
        # TODO: what if font size == 0? the program crashes, no exception is raised
        #self.style.configure(self.str_style + ".Treeview", rowheight=self.tree_item_font["size"])
        self.style.configure(self.str_style + ".Treeview.Heading", font=(None, self.tree_item_font["size"]))
        self.style.configure(self.str_style + ".Treeview.Heading", rowheight=self.tree_item_font["size"])
        self.style.configure(self.str_style + ".Treeview", rowheight=tkFont.Font(font=self.tree_item_font).metrics("linespace"))
        self.SetColumnWidth(self.treeview_columns_dict, self.treeview_column_widths)


class SelectColumnsToDisplay(tk.Toplevel):
    
    def __init__(self, master, dictionary):
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.grab_set()
        self.values = {}
        self.resizable(width=False, height=True)
        self.frame_main = CheckbuttonFrame.CheckboxFrame(self, 0, 0, dictionary, 18, "light gray", "Stupci")
        self.font = tkFont.Font(size=15)

        x = 200
        y = 450
        x_min = 200
        y_min = 450

        self.geometry("{}x{}".format(x, y))
        self.minsize(x_min, y_min)

        self.btn_confirm = tk.Button(
            self,
            text=u"\u2714",
            fg="black",
            bg="lime",
            font=self.font,
            command=lambda: self.Confirm()
        )

        self.btn_confirm.pack(side="top", fill="x")
        self.frame_main.pack(side="top", expand=True, fill="both")

    
    def Confirm(self):
        self.values = self.frame_main.get_values()
        self.destroy()