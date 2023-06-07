import copy
import tkinter as tk
from tkinter import ttk
import ScrollableFrame
from typing import Dict
import tkinter.font as tkFont


class CheckboxFrame(tk.Frame):
    def __init__(self, master, cbx_dict, font_size, color, title, **kwargs):
        super().__init__(master, **kwargs)

        self.chk_on_bg = "yellow"
        self.color = color
        self.frame_main = ScrollableFrame.HorizontalAndVertical(self, **kwargs)
        self.frame_main.pack_propagate(False)
        self.frame_main.configure(bg=color)

        self.frame_main.scrollable_frame.configure(bg=color)
        self.frame_main.canvas.configure(bg=color)

        self.style_Chk = ttk.Style()
        self.style_Chk.configure(color + ".TCheckbutton", font=("Arial", font_size), background=color)

        self.style_Chk_ON = ttk.Style()
        self.style_Chk_ON.configure(
            self.chk_on_bg + color + ".TCheckbutton",
            font=("Arial", font_size),
            background=self.chk_on_bg
        )

        self.style_lbl = ttk.Style()
        self.style_lbl.configure(color + ".TLabel", font=("Arial", font_size, "bold"), background=color)

        self.cbx_dict = cbx_dict
        self.chk_btns = []

        self.title = title
        self.lbl_title = ttk.Label(self.frame_main.scrollable_frame, anchor="w", text=self.title, style=color+".TLabel")
        self.lbl_title.pack(side="top", expand=True, fill="both")

        self.values = []
        self.chk_vars = []

        for key, value in self.cbx_dict.items():
            if value:
                is_selected = 1
            else:
                is_selected = 0

            self.chk_vars.append(tk.IntVar(value=is_selected))

            chk = ttk.Checkbutton(
                self.frame_main.scrollable_frame,
                text=key,
                variable=self.chk_vars[-1],
                style=color + ".TCheckbutton"
            )
            chk.configure(command=lambda x=chk: self.change_bg(x))

            self.chk_btns.append(chk)
            self.chk_btns[-1].pack(side="top", expand=True, fill="both")

            self.frame_main.pack(expand=True, fill="both")

    def change_bg(self, ttk_checkbutton: ttk.Checkbutton):
        if ttk_checkbutton.instate(["selected"]):
            ttk_checkbutton.configure(style=self.chk_on_bg + self.color + ".TCheckbutton")
            return
        ttk_checkbutton.configure(style=self.color + ".TCheckbutton")

    def get_values(self):
        for i, key in enumerate(self.cbx_dict):
            if self.chk_btns[i].instate(["selected"]):
                self.cbx_dict[key] = 1
            else:
                self.cbx_dict[key] = 0
        return self.cbx_dict


class RadiobuttonFrame(tk.Frame):
    def __init__(self, master, width, height, rad_dict, font_size, color, title):
        tk.Frame.__init__(self, master, bg=color, width=width, height=height)

        self.frame_main = ScrollableFrame.HorizontalAndVertical(self, width=width, height=height)
        self.frame_main.pack_propagate(False)
        self.frame_main.configure(bg=color)

        self.frame_main.scrollable_frame.configure(bg=color)
        self.frame_main.canvas.configure(bg=color)

        self.style_Rad = ttk.Style()
        self.style_Rad.configure(color + ".TRadiobutton", font=("Arial", font_size), background=color)

        self.style_lbl = ttk.Style()
        self.style_lbl.configure(color + ".TLabel", font=("Arial", font_size, "bold"), background=color)

        self.rad_dict = rad_dict
        self.rad_btns = []

        self.title = title
        self.lbl_title = ttk.Label(
            self.frame_main.scrollable_frame,
            anchor="w",
            text=self.title,
            style=color + ".TLabel"
        )

        self.lbl_title.pack(side="top", expand=True, fill="both")

        self.values = []
        self.rad_selected = tk.StringVar()

        for key in self.rad_dict:
            rad = ttk.Radiobutton(
                self.frame_main.scrollable_frame,
                text=key,
                value=key,
                variable=self.rad_selected,
                style=color + ".TRadiobutton"
            )

            self.rad_btns.append(rad)
            self.rad_btns[-1].pack(side="top", expand=True, fill="both")
            self.frame_main.pack(expand=True, fill="both")

    def get_values(self):
        return {
            self.rad_selected.get(): 1
        }


class MultiCheckboxFrame(tk.Frame):
    def __init__(self, master, cbx_dict: Dict[str, Dict[str, int]], font_size, color, title, **kwargs):
        tk.Frame.__init__(self, master, bg=color, **kwargs)

        self.bg_colors = {
            True: "#ffffff",
            False: "#aaaaaa"
        }
        self.bg_color_index = True

        self.title = title
        self.font = tkFont.Font(size=font_size, family="Arial")
        self.chk_on_bg = "yellow"
        self.color = color
        self.frame_main = ScrollableFrame.HorizontalAndVertical(self)
        self.frame_main.pack_propagate(False)
        self.frame_main.configure(bg=color)

        self.frame_titles = tk.Frame(self.frame_main.scrollable_frame, bg=color)
        self.frame_titles.rowconfigure(0, weight=1)
        self.frame_operations = tk.Frame(self.frame_main.scrollable_frame, bg=color)
        self.frame_operations.rowconfigure(0, weight=1)
        self.cbx_dict = copy.deepcopy(cbx_dict)
        i = 0
        for i, key in enumerate(self.cbx_dict[next(iter(self.cbx_dict))]):
            lbl = ttk.Label(
                self.frame_titles,
                text=key,
                font=("Arial", font_size),
                justify="center",
                anchor="center",
            )
            lbl.grid(row=0, column=i+1, sticky="ew")
            self.frame_titles.columnconfigure(i+1, weight=self.font.measure(key), uniform="titles_cols")
            self.frame_operations.columnconfigure(i+1, weight=self.font.measure(key), uniform="chks_cols")
        self.cols = i
        self.frame_titles.pack(side="top")

        self.frame_main.scrollable_frame.configure(bg=color)
        self.frame_main.canvas.configure(bg=color)

        self.style_Chk1 = ttk.Style()
        self.style_Chk1.configure(title + self.bg_colors[True] + ".TCheckbutton", font=self.font,
                                  background=self.bg_colors[True])
        self.style_Chk2 = ttk.Style()
        self.style_Chk2.configure(title + self.bg_colors[False] + ".TCheckbutton", font=self.font,
                                  background=self.bg_colors[False])

        self.style_lbl1 = ttk.Style()
        self.style_lbl1.configure(title + self.bg_colors[True] + ".TLabel", font=self.font,
                                  background=self.bg_colors[True])
        self.style_lbl2 = ttk.Style()
        self.style_lbl2.configure(title + self.bg_colors[False] + ".TLabel", font=self.font,
                                  background=self.bg_colors[False])
        self.style_frame1 = ttk.Style()
        self.style_frame1.configure(title + self.bg_colors[True] + ".TFrame", font=self.font,
                                    background=self.bg_colors[True])
        self.style_frame2 = ttk.Style()
        self.style_frame2.configure(title + self.bg_colors[False] + ".TFrame", font=self.font,
                                    background=self.bg_colors[False])

        self.chk_btns = []

        self.lbl_title = ttk.Label(self.frame_titles, anchor="w", text=self.title, style=color + ".TLabel", font=self.font)
        self.lbl_title.grid(row=0, column=0, sticky="nsew")

        self.values = []
        self.chk_vars = []

        self.frames_chks = []

        for key, value in self.cbx_dict.items():
            self.bg_color_index = not self.bg_color_index
            self.frames_chks.append(ttk.Frame(self.frame_operations, style=title + self.bg_colors[self.bg_color_index] + ".TFrame"))
            ttk.Label(
                self.frames_chks[-1],
                anchor="center",
                text=key,
                style=title + self.bg_colors[self.bg_color_index] + ".TLabel"
            ).grid(row=0, column=0, sticky="nsew")
            print(self.bg_colors[self.bg_color_index])
            print(key)
            print(value)
            for i, (k, v) in enumerate(value.items()):
                if v:
                    is_selected = 1
                else:
                    is_selected = 0

                self.chk_vars.append(tk.IntVar(value=is_selected))

                chk = ttk.Checkbutton(
                    self.frames_chks[-1],
                    variable=self.chk_vars[-1],
                    style=title + self.bg_colors[self.bg_color_index] + ".TCheckbutton"
                )

                self.chk_btns.append(chk)
                self.chk_btns[-1].grid(row=0, column=i + 1)

        for i, key in enumerate(self.cbx_dict[next(iter(self.cbx_dict))]):
            for frame in self.frames_chks:
                frame.pack(side="top", fill="x")
                frame.columnconfigure(i+1, weight=self.font.measure(key), uniform="frames_chks_cols")
                frame.columnconfigure(0, weight=self.font.measure(max(cbx_dict.keys())), uniform="frames_chks_cols")  # ispravit

        self.frame_titles.columnconfigure(0, weight=self.font.measure(max(cbx_dict.keys())), uniform="titles_cols")
        self.frame_operations.columnconfigure(0, weight=self.font.measure(max(cbx_dict.keys())), uniform="chks_cols")

        self.frame_operations.pack(side="bottom")
        self.frame_main.pack(expand=True, fill="both")

    def get_values(self):
        row = 0
        for key, value in self.cbx_dict.items():
            for k in value:
                if self.chk_btns[row].instate(["selected"]):
                    self.cbx_dict[key][k] = 1
                else:
                    self.cbx_dict[key][k] = 0
                row += 1
        return self.cbx_dict
