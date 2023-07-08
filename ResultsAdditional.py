import KeepAspectRatio
import tkinter as tk
import tkinter.font as tkFont
from tkinter import colorchooser
import HoverInfo
from Logger import benchmark
import Tools
import Fonts
import Colors


class ResultsAdditional(tk.Frame):
    @benchmark
    def __init__(self, parent, controller, tree, input_frame):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.r_font: tkFont.Font = Fonts.fonts2["Dnevnik"]["tools"]["font"]
        self.r_font_config = Fonts.fonts2["Dnevnik"]["tools"] #tkFont.Font(size=10)
        self.tips = []

        KeepAspectRatio.subscribe(self)

        self.input_frame = input_frame
        self.tree = tree

        self.rowconfigure(0, weight=1)
        for x in range(0, 8, 1):
            self.columnconfigure(x, weight=5, uniform="columns")
        for x in range(6, 15, 1):
            self.columnconfigure(x, weight=1, uniform="columns")
        self.grid_propagate(False)

        self.btn_treeview_select_columns = tk.Button(
            self,
            text=u"\u2261",
            command=lambda: self.SelectColumnsToDisplay(),
            font=self.r_font,
            bd=5
        )
        btn_treeview_select_columns_help_text = "Prikaži/sakrij stupce dnevnika"
        self.btn_treeview_select_columns_help = HoverInfo.create_tooltip(
            widget=self.btn_treeview_select_columns,
            text=btn_treeview_select_columns_help_text,
            font_size=12,
            anchor="n"
        )

        self.btn_filter = tk.Button(
            self,
            text="FILTER",
            bg="white",
            fg="black",
            font=self.r_font,
            command=lambda: self.Filter(),
            bd=5
        )
        btn_filter_help_text = "Filtriraj rezultate u dnevniku"
        self.btn_filter_help = HoverInfo.create_tooltip(
            widget=self.btn_filter,
            text=btn_filter_help_text,
            font_size=12,
            anchor="n"
        )

        self.btn_edit = tk.Button(
            self,
            text=u"\u270D",
            fg="yellow",
            bg="black",
            command=lambda: self.Edit(),
            font=self.r_font,
            bd=5
        )
        btn_help_text = "Uredi odabrani rezultat u dnevniku"
        self.btn_edit_help = HoverInfo.create_tooltip(
            widget=self.btn_edit,
            text=btn_help_text,
            font_size=12,
            anchor="n"
        )

        self.btn_delete = tk.Button(
            self,
            text="DEL",
            fg="red",
            bg="black",
            font=self.r_font,
            command=lambda: self.Delete(),
            bd=5
        )
        btn_delete_help_text = "Obriši odabrani rezulat u dnevniku"
        self.btn_delete_help = HoverInfo.create_tooltip(
            widget=self.btn_delete,
            text=btn_delete_help_text,
            font_size=12,
            anchor="n"
        )

        self.btn_refresh = tk.Button(
            self,
            text=u"\u27f3",
            fg="black",
            command=lambda: self.Refresh(),
            font=self.r_font,
            bd=5
        )
        btn_refresh_help_text = "Ponovno učitaj rezultate"
        self.btn_refresh_help = HoverInfo.create_tooltip(
            widget=self.btn_refresh,
            text=btn_refresh_help_text,
            font_size=12,
            anchor="n",
            orientation="left"
        )

        self.btn_adjust_columns_by_text = tk.Button(
            self,
            text="<--->",
            fg="blue",
            bg="white",
            command=lambda: self.adjust_columns_by_text(),
            bd=5
        )
        btn_adjust_columns_by_text_help_text = """Prilagođava širinu stupca prema najdužoj stavki u njemu"""
        self.btn_adjust_columns_by_text_help = HoverInfo.create_tooltip(
            widget=self.btn_adjust_columns_by_text,
            text=btn_adjust_columns_by_text_help_text,
            font_size=12,
            orientation="left",
            anchor="n"
        )

        self.btn_left_anchor = tk.Button(
            self,
            text="<",
            fg="black",
            font=self.r_font,
            command=lambda: self.set_text_left_anchor()
        )

        self.btn_center_anchor = tk.Button(
            self,
            text="<>",
            fg="black",
            font=self.r_font,
            command=lambda: self.set_text_center_anchor()
        )

        self.btn_right_anchor = tk.Button(
            self,
            text=">",
            fg="black",
            font=self.r_font,
            command=lambda: self.set_text_right_anchor()
        )

        self.btn_results_settings = tk.Button(
            self,
            text=u"\u2699",
            bg="blue",
            fg="yellow",
            command=lambda: ResultsSettingsToplevel(self, self.tree, self.input_frame),
            font=self.r_font,
            bd=5
        )
        btn_results_settings_help_text = "Postavke boje i fontova"
        self.btn_results_settings_help = HoverInfo.create_tooltip(
            widget=self.btn_results_settings,
            text=btn_results_settings_help_text,
            font_size=12,
            orientation="left",
            anchor="n"
        )

        self.btn_adjust_columns_by_text.grid(row=0, column=5, sticky="nsew")
        self.btn_refresh.grid(row=0, column=4, sticky="nsew")
        self.btn_delete.grid(row=0, column=3, sticky="nsew")
        self.btn_edit.grid(row=0, column=2, sticky="nsew")
        self.btn_filter.grid(row=0, column=1, sticky="nsew")
        self.btn_treeview_select_columns.grid(row=0, column=0, sticky="nsew")
        self.btn_results_settings.grid(row=0, column=11, columnspan=2, sticky="nsew")

    def keep_aspect_ratio(self):
        pass

    def hide_input(self):
        self.controller.change_input_visibility()

    def adjust_columns_by_text(self):
        self.controller.AdjustColumnsSizePressed()

    def set_text_right_anchor(self):
        pass

    def set_text_left_anchor(self):
        pass

    def set_text_center_anchor(self):
        pass

    # TODO: merge this class with Results and inject ResutsTree class to it to avoid calling controller

    def Edit(self):
        self.controller.EditPressed()

    def Delete(self):
        self.controller.DeletePressed()

    def SelectColumnsToDisplay(self):
        self.controller.UpdateTreeviewDispayColumns()

    def Filter(self):
        self.controller.FilterPressed()

    def Refresh(self):
        self.controller.RefreshPressed()


class ResultsSettingsToplevel(tk.Toplevel):
    def __init__(self, parent, tree, input_class):
        tk.Toplevel.__init__(self, parent)
        self.wm_transient(parent)
        self.geometry("{}x{}".format(800, 600))
        self.grab_set()
        self.grid_propagate(False)

        self.rowconfigure(0, weight=4, uniform="ResultsSettingsToplevel_rows")
        self.rowconfigure(1, weight=5, uniform="ResultsSettingsToplevel_rows")

        self.columnconfigure(0, weight=1)

        self.frame_input_settings = ResultsInputSettings(self, input_class, "gray40")
        self.frame_treeview_settings = ResultsTreeSettings(self, tree, "gray60")

        self.frame_input_settings.grid(row=0, column=0, sticky="nsew")
        self.frame_treeview_settings.grid(row=1, column=0, sticky="nsew")


class ResultsTreeSettings(tk.Frame):
    def __init__(self, parent, tree, bg="gray"):
        tk.Frame.__init__(self, parent)
        self.tree = tree

        self.font = Fonts.fonts2["Dnevnik"]["unos"]["settings"]["font"]

        self.lbl_title = tk.Label(
            self,
            text="Tablica:",
            font=self.font
        )

        self.btn_even_rows_bg_color = tk.Button(
            self,
            text="Pozadinska boja parnih redova",
            font=self.font,
            command=self.change_even_rows_bg_color
        )

        self.btn_even_rows_fg_color = tk.Button(
            self,
            text="Boja teksta u parnim redovima",
            font=self.font,
            command=self.change_even_rows_fg_color
        )

        self.btn_odd_rows_bg_color = tk.Button(
            self,
            text="Pozadinska boja neparnih redova",
            font=self.font,
            command=self.change_odd_rows_bg_color
        )

        self.btn_odd_rows_fg_color = tk.Button(
            self,
            text="Boja teksta u neparnim redovima",
            font=self.font,
            command=self.change_odd_rows_fg_color
        )

        self.lbl_rows_font = tk.Label(
            self,
            text="Font teksta",
            font=self.font
        )

        self.FontSettings_rows_font = Fonts.FontSettings(
            self,
            font_config=Fonts.fonts2["Dnevnik"]["treeview"],
            notif_func=lambda: KeepAspectRatio.call_subscribers(self.tree.__class__.__name__)
        )

        self.grid_propagate(False)

        self.rowconfigure(0, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(1, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(2, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(3, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(4, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(5, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(6, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(7, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(8, weight=1, uniform="ResultsTreeSettings_rows")
        self.rowconfigure(9, weight=1, uniform="ResultsTreeSettings_rows")
        self.columnconfigure(0, weight=5, uniform="ResultsTreeSettings_cols")
        self.columnconfigure(1, weight=1, uniform="ResultsTreeSettings_cols")
        self.columnconfigure(2, weight=5, uniform="ResultsTreeSettings_cols")

        self.lbl_title.grid(row=0, column=0, rowspan=3, sticky="nsw")
        self.btn_even_rows_bg_color.grid(row=2, column=0, sticky="nsew")
        self.btn_even_rows_fg_color.grid(row=4, column=0, sticky="nsew")
        self.btn_odd_rows_bg_color.grid(row=6, column=0, sticky="nsew")
        self.btn_odd_rows_fg_color.grid(row=8, column=0, sticky="nsew")

        self.lbl_rows_font.grid(row=1, column=2, sticky="sew")
        self.FontSettings_rows_font.grid(row=2, column=2, sticky="nsew")

        self.change_bg_frame_color(bg)

    def change_bg_frame_color(self, color: str):
        self.configure(bg=color)
        self.lbl_title.configure(bg=color)
        self.lbl_rows_font.configure(bg=color)

    def change_even_rows_bg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["treeview"]["even_rows"]["bg"] = color
            Colors.call_subscribers(self.tree)

    def change_even_rows_fg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["treeview"]["even_rows"]["fg"] = color
            Colors.call_subscribers(self.tree)

    def change_odd_rows_bg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["treeview"]["odd_rows"]["bg"] = color
            Colors.call_subscribers(self.tree)

    def change_odd_rows_fg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["treeview"]["odd_rows"]["fg"] = color
            Colors.call_subscribers(self.tree)


class ResultsInputSettings(tk.Frame):
    def __init__(self, parent, input_class, bg="gray"):
        tk.Frame.__init__(self, parent)
        self.input_class = input_class

        self.font = Fonts.fonts2["Dnevnik"]["unos"]["settings"]["font"]

        self.lbl_title = tk.Label(
            self,
            text="Unos:",
            font=self.font
        )

        self.btn_change_bg_color = tk.Button(
            self,
            text="Pozadinska boja",
            font=self.font,
            command=self.change_bg_color
        )

        self.btn_change_fg_color = tk.Button(
            self,
            text="Boja teksta",
            font=self.font,
            command=self.change_fg_color
        )

        self.FontSettings_cbx_lbx_font = Fonts.FontSettings(
            self,
            font_config=Fonts.fonts2["Dnevnik"]["unos"]["combobox_listbox"]
        )

        self.FontSettings_cbx_ent_font = Fonts.FontSettings(
            self,
            font_config=Fonts.fonts2["Dnevnik"]["unos"]["combobox_entry"],
            notif_func=lambda: KeepAspectRatio.call_subscribers("ResultsInput")
        )

        self.FontSettings_lbl_font = Fonts.FontSettings(
            self,
            font_config=Fonts.fonts2["Dnevnik"]["unos"]["labels"]
        )

        self.lbl_cbx_lbx_font = tk.Label(
            self,
            text="Font padajućeg izbornika",
            font=self.font
        )

        self.lbl_cbx_ent_font = tk.Label(
            self,
            text="Font unosa",
            font=self.font
        )

        self.lbl_lbl_font = tk.Label(
            self,
            text="Font naslova",
            font=self.font
        )

        self.grid_propagate(False)

        self.rowconfigure(0, weight=3, uniform="ResultsInputSettings_rows")
        self.rowconfigure(1, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(2, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(3, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(4, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(5, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(6, weight=1, uniform="ResultsInputSettings_rows")
        self.rowconfigure(7, weight=1, uniform="ResultsInputSettings_rows")
        self.columnconfigure(0, weight=5, uniform="ResultsInputSettings_cols")
        self.columnconfigure(1, weight=1, uniform="ResultsInputSettings_cols")
        self.columnconfigure(2, weight=5, uniform="ResultsInputSettings_cols")

        self.lbl_title.grid(row=0, column=0, columnspan=3, sticky="nsw")
        self.btn_change_bg_color.grid(row=2, column=0, sticky="nsew")
        self.btn_change_fg_color.grid(row=4, column=0, sticky="nsew")
        self.lbl_cbx_ent_font.grid(row=1, column=2, sticky="sew")
        self.FontSettings_cbx_ent_font.grid(row=2, column=2, sticky="nsew")
        self.lbl_lbl_font.grid(row=5, column=2, sticky="sew")
        self.FontSettings_lbl_font.grid(row=6, column=2, sticky="nsew")

        self.change_bg_frame_color(bg)

    def change_bg_frame_color(self, color: str):
        self.configure(bg=color)
        self.lbl_title.configure(bg=color)
        self.lbl_lbl_font.configure(bg=color)
        self.lbl_cbx_lbx_font.configure(bg=color)
        self.lbl_cbx_ent_font.configure(bg=color)

    def change_bg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["input"]["bg"] = color
            Colors.call_subscribers(self.input_class)

    def change_fg_color(self):
        color = Tools.color_picker()
        if color:
            Colors.colors["Results"]["input"]["fg"] = color
            Colors.call_subscribers(self.input_class)


class ResultsColorPicker(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.btn_input_bg_color = tk.Button(
            self,
            text="Pozadinska boja unosa",
            command=self.change_input_bg_color
        )

        self.btn_input_text_color = tk.Button(
            self,
            text="Boja teksta unosa",
            command=self.change_input_text_color
        )

        self.btn_tree_odd_color = tk.Button(
            self,
            text="Boja neparnih redova",
            command=self.change_tree_odd_rows_bg_color
        )

        self.btn_tree_odd_text_color = tk.Button(
            self,
            text="Boja teksta u neparnim redovima",
            command=self.change_tree_odd_rows_text_color
        )

        self.btn_tree_even_color = tk.Button(
            self,
            text="Boja parnih redova",
            command=self.change_tree_even_rows_bg_color
        )

        self.btn_tree_even_text_color = tk.Button(
            self,
            text="Boja teksta u parnim redovima",
            command=self.change_tree_even_rows_text_color
        )

        self.rowconfigure(0, weight=1, uniform="rows")
        self.rowconfigure(1, weight=3, uniform="rows")
        self.rowconfigure(2, weight=1, uniform="rows")
        self.rowconfigure(3, weight=3, uniform="rows")
        self.rowconfigure(4, weight=1, uniform="rows")
        self.rowconfigure(5, weight=3, uniform="rows")
        self.rowconfigure(6, weight=1, uniform="rows")
        self.rowconfigure(7, weight=3, uniform="rows")
        self.rowconfigure(8, weight=1, uniform="rows")
        self.rowconfigure(9, weight=3, uniform="rows")
        self.rowconfigure(10, weight=1, uniform="rows")
        self.rowconfigure(11, weight=3, uniform="rows")
        self.rowconfigure(12, weight=1, uniform="rows")

        self.columnconfigure(0, weight=1, uniform="cols")
        self.columnconfigure(1, weight=5, uniform="cols")
        self.columnconfigure(2, weight=1, uniform="cols")

        self.btn_input_bg_color.grid(row=1, column=1, sticky="nsew")
        self.btn_input_text_color.grid(row=3, column=1, sticky="nsew")
        self.btn_tree_odd_color.grid(row=5, column=1, sticky="nsew")
        self.btn_tree_odd_text_color.grid(row=7, column=1, sticky="nsew")
        self.btn_tree_even_color.grid(row=9, column=1, sticky="nsew")
        self.btn_tree_even_text_color.grid(row=11, column=1, sticky="nsew")

        self.grid_propagate(False)

    def change_input_bg_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_input_bg_color(color)

    def change_input_text_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_input_text_color(color)

    def change_tree_odd_rows_bg_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_tree_odd_rows_bg_color(color)

    def change_tree_even_rows_bg_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_tree_even_rows_bg_color(color)

    def change_tree_odd_rows_text_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_tree_odd_rows_text_color(color)

    def change_tree_even_rows_text_color(self):
        color = Tools.color_picker()
        if color:
            self.controller.change_tree_even_rows_text_color(color)
