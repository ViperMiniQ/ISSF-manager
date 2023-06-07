# NEED TO BE CALLED BEFORE ANY OTHER MODULE LOADS THAT IS USING FONTS
import tkinter.font as tkFont

import ApplicationProperties
import ScrollableFrame
# import dbcommands
import KeepAspectRatio
import tkinter as tk
from tkinter import ttk
import JSONManager
import jsonTypes
import HoverInfo
from typing import List

_available_fonts = []

_fonts_settings = JSONManager.load_json(ApplicationProperties.FONTS_PATH)  # dbcommands.db.fonts_configuration


def _get_font(font_config: jsonTypes.FontSettings, fullscreen_size=0) -> tkFont.Font:
    font = tkFont.Font()
    font.configure(
        family=font_config["family"],
        weight=font_config["weight"],
        underline=font_config["underline"],
        slant=font_config["slant"],
        overstrike=font_config["overstrike"],
        size=font_config["size"] if not fullscreen_size else int(fullscreen_size / font_config["divisor"])
    )
    return font


fonts2 = JSONManager.load_json(ApplicationProperties.FONTS_PATH)

# fonts2 = {}


def _get_font_settings(font: tkFont.Font) -> jsonTypes.FontSettings:
    font_settings: jsonTypes.FontSettings = {
        "size": font["size"],
        "slant": font["slant"],
        "overstrike": font["overstrike"],
        "underline": font["underline"],
        "family": font["family"],
        "weight": font["weight"]
    }
    return font_settings


def configure_fonts2_for_save(current):
    for key, value in current.items():
        if not isinstance(value, dict):
            try:
                font_settings = _get_font_settings(current["font"])

                if ApplicationProperties.RESPECT_FONTS_DIVISOR:
                    divisor = int(KeepAspectRatio.x / font_settings["size"])
                else:
                    divisor = current['divisor']

                for key2 in list(current.keys()):
                    current.pop(key2)
                current.update(font_settings)
                current["divisor"] = divisor
                return
            except:
                return
        configure_fonts2_for_save(value)


def save_fonts2_config(save_as_is: bool = False):
    global fonts2
    if not save_as_is:
        configure_fonts2_for_save(fonts2)
    JSONManager.save_json(ApplicationProperties.FONTS_PATH, fonts2)


def load_fonts_needs_better_name(current, fullscreen_size=0):
    for key, value in current.items():
        if not isinstance(value, dict):
            current["font"] = _get_font(current, fullscreen_size)
            return
        load_fonts_needs_better_name(value, fullscreen_size)


def load_fonts2(fullscreen_size=0):
    global fonts2
    load_fonts_needs_better_name(fonts2, fullscreen_size)


def refresh_available_fonts():
    global _available_fonts
    _available_fonts = tkFont.families()


def get_available_fonts():
    refresh_available_fonts()
    return _available_fonts


class FontAdjuster(object):
    def __init__(self):
        pass

    def adjust_all_fonts_by_divisor(self, current):
        for key, value in current.items():
            if not isinstance(value, dict):
                if current["divisor"]:
                    current["font"].configure(size=int(KeepAspectRatio.x / current["divisor"]))
                    return
            self.adjust_all_fonts_by_divisor(value)

    def keep_aspect_ratio(self):
        global fonts2
        self.adjust_all_fonts_by_divisor(fonts2)


class FontSettings(tk.Frame):
    def __init__(self, parent, font_config, notif_func=None):#, font: tkFont.Font = tkFont.Font(size=14)):
        tk.Frame.__init__(self, parent)
        self.font_config = font_config
        self.notif_func = notif_func

        self.font = tkFont.Font(size=12)

        self.option_add("*TCombobox*Listbox*Font", self.font)
        self.font_size = tk.IntVar()

        self.tooltips = []

        self.font_state = tk.IntVar()

        self.cbx_family = ttk.Combobox(
            self,
            values=get_available_fonts(),
            font=self.font,
            state="readonly"
        )
        self.cbx_family.set(self.font_config["font"]["family"])

        self.spin_size = tk.Spinbox(
            self,
            state="readonly",
            from_=4,
            to=42,
            textvariable=self.font_size
        )
        self.font_size.set(self.font_config["font"]["size"])

        self.btn_weight = tk.Button(
            self,
            text="B",
            font=self.font,
            command=self.weight_change
        )
        if self.font_config["font"]["weight"] == "bold":
            self.btn_weight.configure(relief="sunken")

        self.btn_slant = tk.Button(
            self,
            text="I",
            font=self.font,
            command=self.slant_change
        )
        if self.font_config["font"]["slant"] == "italic":
            self.btn_slant.configure(relief="sunken")

        self.btn_underline = tk.Button(
            self,
            text="U",
            font=self.font,
            command=self.underline_change
        )
        if self.font_config["font"]["underline"]:
            self.btn_underline.configure(relief="sunken")

        self.btn_mode = tk.Button(
            self,
            text="D",
            font=self.font,
            command=self.mode_change
        )
        if not self.font_config["divisor"]:
            self.btn_mode.configure(text="S")
        btn_mode_help_text = """S(tatičan) - veličina ostaje ista bez obzira na veličinu prozora aplikacije
D(inamičan) - veličina se mijenja proporcionalno veličini prozora aplikacije"""
        self.btn_mode_help = HoverInfo.create_tooltip(
            widget=self.btn_mode,
            text=btn_mode_help_text,
            font_size=12,
            anchor="w",
            orientation="left"
        )
        self.tooltips.append(self.btn_mode_help)

        self.grid_propagate(False)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5, uniform="FontSettings_cols")
        self.columnconfigure(1, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(2, weight=2, uniform="FontSettings_cols")
        self.columnconfigure(3, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(4, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(5, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(6, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(7, weight=1, uniform="FontSettings_cols")
        self.columnconfigure(8, weight=1, uniform="FontSettings_cols")

        self.cbx_family.grid(row=0, column=0, sticky="nsew")
        self.spin_size.grid(row=0, column=2, sticky="nsew")
        self.btn_weight.grid(row=0, column=4, sticky="nsew")
        self.btn_slant.grid(row=0, column=5, sticky="nsew")
        self.btn_underline.grid(row=0, column=6, sticky="nsew")
        self.btn_mode.grid(row=0, column=8, sticky="nsew")

        self.load_font_settings()

        if self.notif_func is not None:
            self.cbx_family.bind("<<ComboboxSelected>>", self.family_change_and_notif)
            self.spinbox_validation = (self.register(self.size_change_and_notif))
            self.btn_weight.configure(command=self.weight_change_and_notif)
            self.btn_slant.configure(command=self.slant_change_and_notif)
            self.btn_underline.configure(command=self.underline_change_and_notif)
            self.btn_mode.configure(command=self.mode_change_and_notif)
        else:
            self.spinbox_validation = (self.register(self.size_change))
            self.cbx_family.bind("<<ComboboxSelected>>", self.family_change)
        self.spin_size.configure(validate="all", validatecommand=(self.spinbox_validation, "%P"))

    def bind_to_notif_func(self):
        self.cbx_family.bind("<<ComboboxSelected>>", self.notif_func, add="+")

    def size_change_and_notif(self, value=None):
        self.size_change(value)
        self.notif_func()
        return True

    def load_font_settings(self):
        pass

    def mode_change_and_notif(self):
        self.mode_change()
        self.notif_func()

    def mode_change(self):
        if self.btn_mode["text"] == "D":
            self.font_config["divisor"] = 0
            self.btn_mode.configure(text="S")
        else:
            self.font_config["divisor"] = KeepAspectRatio.x // int(self.spin_size.get())
            self.btn_mode.configure(text="D")

    def refresh_font_families(self):
        self.cbx_family.configure(values=get_available_fonts())

    def bind_to_changes(self):
        self.spin_size.configure(validate="all", validatecommand=(self.spinbox_validation, "%P"))

    def size_change(self, value) -> bool:
        self.font_config["font"].configure(size=int(self.font_size.get()))
        if self.btn_mode["text"] == "D":
            self.font_config["divisor"] = KeepAspectRatio.x // int(self.spin_size.get())
        return True

    def family_change_and_notif(self, event=None):
        self.family_change()
        self.notif_func()

    def family_change(self, event=None):
        self.font_config["font"].configure(family=self.cbx_family.get())
        return True

    def weight_change_and_notif(self):
        self.weight_change()
        self.notif_func()

    def weight_change(self):
        if self.font_config["font"]["weight"] == "normal":
            self.btn_weight.configure(relief="sunken")
            self.font_config["font"]["weight"] = "bold"
        else:
            self.btn_weight.configure(relief="raised")
            self.font_config["font"]["weight"] = "normal"

    def slant_change_and_notif(self):
        self.slant_change()
        self.notif_func()

    def slant_change(self):
        if self.font_config["font"]["slant"] == "roman":
            self.btn_slant.configure(relief="sunken")
            self.font_config["font"]["slant"] = "italic"
        else:
            self.btn_slant.configure(relief="raised")
            self.font_config["font"]["slant"] = "roman"

    def underline_change_and_notif(self):
        self.underline_change()
        self.notif_func()

    def underline_change(self):
        if not self.font_config["font"]["underline"]:
            self.btn_underline.configure(relief="sunken")
            self.font_config["font"]["underline"] = 1
        else:
            self.btn_underline.configure(relief="raised")
            self.font_config["font"]["underline"] = 0

    def destroy(self):
        for tooltip in self.tooltips:
            HoverInfo.remove_tooltip(tooltip)
        tk.Frame.destroy(self)


class AllFontConfiguratorToplevel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("{}x{}".format(500, 600))

        self.frame_main = AllFontConfigurator(self)
        self.frame_main.pack(expand=True, fill="both")


class AllFontConfigurator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.font = tkFont.Font(size=20)

        self.bg_colors = {
            True: "#0055ff",
            False: "#ffffff"
        }
        self.bg_color = True

        self.frame_main = ScrollableFrame.Vertical(self)
        self.frame_main.pack(expand=True, fill="both")

        self.load_fonts(fonts2)

    def add_label(self, text: str):
        tk.Label(
            self.frame_main.scrollable_frame,
            text=text,
            font=self.font
        ).pack(side="top", expand=True, fill="x")

    def add_font_configurator(self, title: str, font_dict):
        f = FontSettingsWithTitle(self.frame_main.scrollable_frame, font_dict, title)
        f.configure(height=50, bd=10, bg=self.bg_colors[self.bg_color])
        f.lbl_title.configure(bg=self.bg_colors[self.bg_color])
        f.pack(side="top", fill="x")
        self.bg_color = not self.bg_color

    def load_fonts(self, current, previous=None, title: List = []):
        if previous:
            title.append(previous)
        for key, value in current.items():
            if not isinstance(value, dict):
                self.add_font_configurator(title=" - ".join(title if title else ["prazno"]), font_dict=current)
                if title:
                    title.pop()
                return
            self.load_fonts(value, key, title)
            if key in title:
                if title:
                    title.pop()


class FontSettingsWithTitle(FontSettings):
    def __init__(self, parent, font_config, title: str, notif_func=None):
        super().__init__(parent, font_config, notif_func)

        self.font = tkFont.Font(size=14)

        self.columnconfigure(9, weight=14, uniform="FontSettings_cols")

        self.lbl_title = tk.Label(
            self,
            text=title,
            font=self.font,
            anchor="w"
        )

        self.lbl_title.grid(row=0, column=9, sticky="nsew")