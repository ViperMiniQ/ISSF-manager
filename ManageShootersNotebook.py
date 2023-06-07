import tkinter as tk
from tkinter import ttk
import Fonts
import ManageShootersInfoGeneral
import ManageShootersInfoContact
import ManageShootersInfoPIN
import ManageShootersInfoRequired
import ManageShooterInfoNotes
import ManageShootersWeapons
from dbcommands_rewrite import DBGetter, DBUpdate


class ManageShootersInformation(tk.Frame):
    def __init__(self, parent, sql, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.controller = parent
        self.notebook_add_shooter = ttk.Notebook(self)
        self.pack_propagate(False)

        self.font_btns = Fonts.fonts2["ManageShooters"]["ManageShootersInformation"]["buttons"]["font"]

        self.btn_save_changes = tk.Button(
            self,
            text="Spremi promjene",
            bg="green",
            fg="black",
            font=self.font_btns,
            command=self.save_shooter_details
        )

        self.frame_info_required = ManageShootersInfoRequired.ShooterRequiredInformation(self.notebook_add_shooter)
        self.frame_info_required.grid_propagate(False)
        self.frame_info_required.pack_propagate(False)
        self.frame_info_PIN = ManageShootersInfoPIN.ShooterPINInformation(self.notebook_add_shooter)
        self.frame_info_basic = ManageShootersInfoGeneral.ShooterInfoBasic(self.notebook_add_shooter)
        self.frame_info_contact = ManageShootersInfoContact.ShooterInfoContact(self.notebook_add_shooter)
        self.frame_info_notes = ManageShooterInfoNotes.ShooterNotes(self.notebook_add_shooter, self.controller)
        self.frame_weapons = ManageShootersWeapons.ShooterWeapons(self.notebook_add_shooter)

        self.notebook_add_shooter.add(self.frame_info_required, text="Obvezno")
        self.notebook_add_shooter.add(self.frame_info_PIN, text="Osobna")
        self.notebook_add_shooter.add(self.frame_info_basic, text="Opće")
        self.notebook_add_shooter.add(self.frame_info_contact, text="Kontakt")
        self.notebook_add_shooter.add(self.frame_info_notes, text="Napomene")
        self.notebook_add_shooter.add(self.frame_weapons, text="Oružje")

        self.notebook_add_shooter.grid_propagate(False)
        self.notebook_add_shooter.pack_propagate(False)
        self.notebook_add_shooter.propagate(False)

        self.notebook_add_shooter.pack(side="top", expand=True, fill="both")
        self.btn_save_changes.pack(side="bottom", fill="x")

    def save_shooter_details(self):
        self.controller.SaveShooterDetails()

    def SaveShooterDetails(self, shooter_id: int):
        DBUpdate.update_shooter_required_info(shooter_id=shooter_id, values=self.frame_info_required.get_values())
        DBUpdate.update_shooter_PIN_info(shooter_id=shooter_id, values=self.frame_info_PIN.get_values())
        DBUpdate.update_shooter_general_info(shooter_id=shooter_id, values=self.frame_info_basic.get_values())
        DBUpdate.update_shooter_contact_info(shooter_id=shooter_id, values=self.frame_info_contact.get_values())

    def UpdateShooterDetails(self, shooter_id: int):
        self.frame_info_required.UpdateValues(DBGetter.get_shooter_required_info(shooter_id))
        self.frame_info_PIN.UpdateValues(DBGetter.get_shooter_PIN_info(shooter_id))
        self.frame_info_basic.UpdateValues(DBGetter.get_shooter_general_info(shooter_id))
        self.frame_info_contact.UpdateValues(DBGetter.get_shooter_contact_info(shooter_id))
        self.frame_info_notes.UpdateValues()
        self.frame_weapons.set_shooter_id_and_refresh(shooter_id)
