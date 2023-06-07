import tkinter as tk
from tkinter import ttk
import SettingsResults
import SettingsNotifications
import Colors
import Fonts 


class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.font = Fonts.fonts2["Settings"]["buttons"]["font"]

        self.currently_selected_frame = None

        self.frames = {}

        self.container_fullscreen = False

        self.pan = ttk.PanedWindow(self, orient=tk.HORIZONTAL)

        self.pack_propagate(False)
        self.pan.pack(expand=True, fill="both")

        self.container = tk.Frame(self.pan, bg="yellow")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frame_buttons = tk.Frame(self, bd=10, bg="blue4")
        self.btns_frame_buttons = []

        self.btn_hide_frame_buttons = tk.Button(
            self,
            text="<",
            fg="white",
            bg="black",
            command=self.btn_hide_press
        )

        for page in (
                SettingsResults.ModifyResults,
                SettingsNotifications.ModifyNotifications,
        ):
            name = page.__name__
            frame = page(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.btn_results = tk.Button(
            self.frame_buttons,
            text="Dnevnik",
            font=self.font,
            command=lambda: self.show_class("ModifyResults")
        )
        self.btns_frame_buttons.append(self.btn_results)

        self.btn_arms = tk.Button(
            self.frame_buttons,
            text="Oružje",
            font=self.font,
            command=lambda: self.show_class("ModifyArms")
        )
        self.btns_frame_buttons.append(self.btn_arms)

        self.btn_shooters = tk.Button(
            self.frame_buttons,
            text="Strijelci",
            font=self.font,
            command=lambda: self.show_class("ModifyShooters")
        )
        self.btns_frame_buttons.append(self.btn_shooters)

        self.btn_notifications = tk.Button(
            self.frame_buttons,
            text="Obavijesti",
            font=self.font,
            command=lambda: self.show_class("ModifyNotifications")
        )
        self.btns_frame_buttons.append(self.btn_notifications)

        self.btn_seasons = tk.Button(
            self.frame_buttons,
            text="Sezone",
            font=self.font,
            command=lambda: self.show_class("Seasons")
        )
        self.btns_frame_buttons.append(self.btn_seasons)

        self.pan.add(self.frame_buttons, weight=1)
        self.pan.add(self.container, weight=10)
        self.FrameButtons()
        self.color_buttons()

    def btn_hide_press(self, event=None):
        if self.container_fullscreen:
            self.show_frame_buttons()
            self.btn_hide_frame_buttons.configure(text="<")
        else:
            self.hide_frame_buttons()
            self.btn_hide_frame_buttons.configure(text=">")

    def hide_frame_buttons(self, event=None):
        self.frame_buttons.grid_forget()
        self.btn_hide_frame_buttons.grid_forget()
        self.container.grid_forget()
        self.btn_hide_frame_buttons.grid(column=0, row=0, sticky="nsew")
        self.container.grid(column=1, columnspan=3, row=0, sticky="nsew")
        self.container_fullscreen = True

    def show_frame_buttons(self, event=None):
        self.container.grid_forget()
        self.btn_hide_frame_buttons.grid_forget()
        self.frame_buttons.grid(column=0, columnspan=2, row=0, sticky="nsew")
        self.btn_hide_frame_buttons.grid(column=2, row=0, sticky="nsew")
        self.container.grid(column=3, row=0, sticky="nsew")
        self.container_fullscreen = False

    def color_buttons(self, name=None): # TODO: better design color_buttons
        for button in self.btns_frame_buttons:
            button.configure(bg=Colors.colors["Settings"]["buttons"]["off"]["bg"])

        if name == "ModifyResults":
            self.btn_results.configure(bg=Colors.colors["Settings"]["buttons"]["on"]["bg"])
        elif name == "ModifyShooters":
            self.btn_shooters.configure(bg=Colors.colors["Settings"]["buttons"]["on"]["bg"])
        elif name == "ModifyArms":
            self.btn_arms.configure(bg=Colors.colors["Settings"]["buttons"]["on"]["bg"])
        elif name == "ModifyNotifications":
            self.btn_notifications.configure(bg=Colors.colors["Settings"]["buttons"]["on"]["bg"])

    def show_class(self, name):
        self.currently_selected_frame = self.frames[name]
        self.currently_selected_frame.tkraise()
        try:
            self.currently_selected_frame.save_changes()
        except:
            pass
        self.color_buttons(name)

    def FrameButtons(self):
        self.frame_buttons.columnconfigure(0, weight=1, uniform="frame_buttons_columns")
        self.frame_buttons.columnconfigure(1, weight=7, uniform="frame_buttons_columns")
        self.frame_buttons.columnconfigure(2, weight=1, uniform="frame_buttons_columns")
        for x in range(0, 20, 2):
            self.frame_buttons.rowconfigure(x, weight=1, uniform="frame_buttons_rows")
            self.frame_buttons.rowconfigure(x+1, weight=5, uniform="frame_buttons_rows")
        for x, button in enumerate(self.btns_frame_buttons):
            button.grid(row=(x*2)+1, column=1, sticky="nsew")
