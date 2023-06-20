import tkinter as tk
import ManageShootersCommands
import ManageShootersImage
import ManageShootersList
import ManageShootersNotebook
from dbcommands_rewrite import DBGetter


class ManageShooters(tk.Frame):
    current_shooter_id: int = 0

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.managed_frames = []

        self.shooter_details_visible = False
        self.x = 800
        self.y = 450
        self.aspect_ratio = 16/9

        #self.current_shooter_id = 0

        # <GRID> #
        self.grid_columnconfigure(0, weight=15, uniform="manage_shooters_columns")
        self.grid_columnconfigure(1, weight=9, uniform="manage_shooters_columns")
        self.grid_columnconfigure(2, weight=16, uniform="manage_shooters_columns")

        self.grid_rowconfigure(0, weight=7, uniform="manage_shooters_rows")
        self.grid_rowconfigure(1, weight=8, uniform="manage_shooters_rows")
        self.grid_propagate(False)

        self.grid_propagate(False)
        # </GRID> #

        ################################################################################
        #                           #                      #        Combobox           #
        #                           #                      #############################
        #                           #                      #                           #
        #                           #         Image        #         Listbox           #
        #                           #                      #                           #
        #                           #                      #############################
        #           Notebook        #                      #    ADD  #  SHOW  # DELETE #
        #                           ####################################################
        #                           #                      TITLE                       #
        #                           #                                                  #
        #                           #                                                  #
        #                           #                                                  #
        #                           #                     COMMANDS                     #
        #                           #                                                  #
        #                           #                                                  #
        #                           #                                                  #
        ################################################################################

        self.shooter_details = ManageShootersNotebook.ManageShootersInformation(self, None, bd=5, relief="raised")

        self.managed_frames.append(self.shooter_details)
        self.shooter_image = ManageShootersImage.ShooterImage(self)

        self.managed_frames.append(self.shooter_image)
        self.shooter_commands = ManageShootersCommands.ShooterCommands(self)

        self.managed_frames.append(self.shooter_commands)
        self.list_of_shooters = ManageShootersList.ShootersList(self)
        self.list_of_shooters.grid(row=0, column=2, sticky="nsew")
        self.managed_frames.append(self.list_of_shooters)

        self.list_of_shooters.set_notify_function(self.shooter_change)

    def shooter_change(self, shooter_id: int = None):
        if shooter_id is not None:
            self.ShooterInFocusChange(self.current_shooter_id)
            return
        self.ShooterInFocusChange(self.list_of_shooters.get_selected_item_id())

    def place_shooter_details_frames(self):
        self.shooter_details.grid(row=0, rowspan=2, column=0, sticky="nsew")
        self.shooter_image.grid(row=0, column=1, sticky="nsew")
        self.shooter_commands.grid(row=1, column=1, columnspan=2, sticky="nsew")

    def ShooterInFocusChange(self, shooter_id: int):
        if not self.shooter_details_visible:
            self.place_shooter_details_frames()
            self.shooter_details_visible = True
        ManageShooters.current_shooter_id = shooter_id
        self.current_shooter_id = shooter_id
        self.shooter_image.ready_image_select()

        self.LoadShooterDetails(shooter_id)

    def SaveShooterDetails(self):
        self.shooter_details.SaveShooterDetails(self.current_shooter_id)
        self.LoadShooterDetails(self.current_shooter_id)  # trigger refresh right after saving

    def LoadShooterDetails(self, shooter_id: int):
        self.shooter_details.UpdateShooterDetails(shooter_id)

        shooter_basic_info = DBGetter.get_shooter_basic_info(shooter_id)
        self.shooter_commands.update_values(
            title=shooter_basic_info['Ime'] + " " + shooter_basic_info['Prezime'] + " (" + shooter_basic_info['Datum'] + ")",
        )
        self.shooter_image.UpdateValues(shooter_id)
