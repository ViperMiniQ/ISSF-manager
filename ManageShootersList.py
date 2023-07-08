import copy
import tkinter as tk
import tkinter.font as tkFont
import CheckbuttonFrame
import ManageShootersCommands
import Tools
import ToplevelNewShooter
import Changes
from tkinter import messagebox
import ComboboxBasicManager
import Fonts
from dbcommands_rewrite import DBGetter, DBRemover, DBMisc, DBUpdate


class ShootersList(ComboboxBasicManager.ItemBasicManager):
    def __init__(self, parent):
        ComboboxBasicManager.ItemBasicManager.__init__(self, parent)
        cbx_values = ['Svi', 'Bivši članovi']

        self.lbx_menu = tk.Menu(self, font=Fonts.fonts2["ManageShooters"]["list"]["menu"]["font"], tearoff=0)
        self.lbx_menu.add_command(label="Prikaži sve liječničke", command=lambda: ManageShootersCommands.AllDoctorsPDFToplevel(self))
        self.lbx_menu.add_command(label="Prikaži sve registracije", command=lambda: ManageShootersCommands.AllShooterSeasonsToplevel(self))
        self.lbx_menu.add_command(label="Konfiguracija obavijesti svih strijelaca", command=lambda: ShooterNotificationsSettingsToplevel(self))
        self.lbx_menu.add_separator()
        self.lbx_menu.add_separator()
        self.lbx_menu.add_command(label="Prikaži informacije", command=self.notify)
        self.lbx_menu.add_command(label="Ukloni osjetljive informacije", command=self.delete_shooter_hss_info)
        self.lbx_menu.add_command(label="Ukloni sve zapise strijelca u dnevniku", command=self.delete_shooter_results)
        self.lbx_menu.add_separator()
        self.lbx_menu.add_command(label="Umirovi (prebaci u bivše članove)", command=self.retire_shooter)
        self.lbx_menu.add_separator()
        self.lbx_menu.add_command(label="Trajno ukloni strijelca", command=self.delete_shooter)
        self.lbx.assign_menu(self.lbx_menu)

        self.set_combobox_entry_font(Fonts.fonts2["ManageShooters"]["list"]["combobox_entry"]["font"])
        self.set_button_font(Fonts.fonts2["ManageShooters"]["list"]["buttons"]["font"])
        self.set_listbox_font(Fonts.fonts2["ManageShooters"]["list"]["listbox"]["font"])

        self._refresh_cbx_values(cbx_values)
        self._update_values()

    def delete_shooter_results(self):
        ask = tk.messagebox.askyesno(
            title="Ukloni zapise strijelca u dnevniku",
            message=f"Jeste li sigurni da želite obrisati SVE zapise strijelca {self.get_item_in_focus()} u dnevniku?"
        )
        if ask:
            DBRemover.delete_all_shooter_results(self.get_selected_item_id())

    def delete_shooter(self):
        ask = tk.messagebox.askyesnocancel(
            title="Trajno ukloni strijelca",
            message="Trajno uklanjanje strijelca će obrisati sve informacije vezane uz strijelca (uključujući i zapise u dnevniku). Želite li nastaviti?"
        )
        if not ask:
            return
        last_ask = tk.messagebox.askyesno(
            title="Trajno ukloni strijelca",
            message=f"Jeste li sigurni da želite ukloniti sve informacije vezane uz strijelca {self.get_item_in_focus()}?"
        )
        if last_ask:
            DBRemover.delete_shooter_additional_info(shooter_id=self.get_selected_item_id())
            DBRemover.delete_all_shooter_results(shooter_id=self.get_selected_item_id())
            DBRemover.delete_shooter(shooter_id=self.get_selected_item_id())
            Changes.set_shooters()
            self.refresh()
            self.notify()

    def delete_shooter_hss_info(self):
        ask = tk.messagebox.askyesno(
            title="Obriši osjetljive informacije strijelca",
            message=f"Jeste li sigurni da želite obrisati osjetljive informacije strijelca {self.get_item_in_focus()}?"
        )
        if ask:
            DBRemover.delete_shooter_additional_info(self.get_selected_item_id())
            self.refresh()
            self.notify()

    def activate_shooter(self):
        DBMisc.move_shooter_from_retired_to_active(self.get_selected_item_id())
        self.refresh()

    def retire_shooter(self):
        ask = tk.messagebox.askyesno(
            title="Umirovi strijelca",
            message=f"Jeste li sigurno da želite prebaciti strijelca {self.get_item_in_focus()} u umirovljenje strijelce?",
        )
        if ask:
            DBMisc.retire_shooter(self.get_selected_item_id())
            self.refresh()

    def refresh(self):
        self._update_values()

    def _update_values(self, event=None):
        self.shooters = {}
        self._clear_lbx()
        try:
            self.lbx_menu.delete("Učini stalnim članom")
        except Exception:
            pass
        if self.cbx.get() == "Bivši članovi":
            shooters = DBGetter.get_retired_shooters()
            self.lbx_menu.add_command(label="Učini stalnim članom", command=self.activate_shooter)
        else:
            shooters = DBGetter.get_active_shooters() + DBGetter.get_inactive_shooters()
        for shooter in shooters:
            date = Tools.SQL_date_format_to_croatian(shooter['Datum'])
            lbx_shooter = f"{shooter['Ime']} {shooter['Prezime']} ({date})"
            self.items[lbx_shooter] = shooter['id']
            self._append_to_lbx(lbx_shooter)

    def _add_new(self):
        new_shooter = ToplevelNewShooter.AddShooter(self)
        new_shooter.focus()
        new_shooter.wait_window()
        self._update_values()
        Changes.set_shooters()


class ShootersNotificationSetter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        notif_settings = DBGetter.get_all_shooters_notifications()

        self.font = tkFont.Font(size=14)

        self.old_values = {}
        self.values = {}

        for n in notif_settings:
            self.values[f"{n['Ime']} {n['Prezime']}"] = {
                "Osobna": n['Osobna'],
                "Putovnica": n['Putovnica'],
                "Liječnički": n['Lijecnicki'],
                "Rođendan": n['Rodjendan']
            }
        self.frame_main = CheckbuttonFrame.MultiCheckboxFrame(self, self.values, 24, "#ffffff", "Obavijesti")

        self.old_values = copy.deepcopy(self.values)

        for n in notif_settings:
            self.old_values[f"{n['Ime']} {n['Prezime']}"]["id"] = n['id']

        self.btn_save_changes = tk.Button(
            self,
            text="Spremi promjene",
            bg="lime",
            fg="black",
            font=self.font,
            command=lambda: self.save_changes()
        )

        self.btn_save_changes.pack(side="top")
        self.frame_main.pack(side="top", expand=True, fill="both")

    def check_for_changes(self):
        if self.frame_main.get_values() == self.values:
            return False
        return True

    def save_changes(self):
        if self.check_for_changes():
            new_values = self.frame_main.get_values()
            for name, values in new_values.items():
                DBUpdate.update_shooter_notifications(
                    shooter_id=self.old_values[name]["id"],
                    doctor=new_values[name]['Liječnički'],
                    NPIN=new_values[name]["Osobna"],
                    passport=new_values[name]["Putovnica"],
                    birthday=new_values[name]["Rođendan"]
                )


class ShooterNotificationsSettingsToplevel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("{}x{}".format(800, 600))

        self.frame_main = ShootersNotificationSetter(self)
        self.frame_main.pack(expand=True, fill="both")

        self.protocol("WM_DELETE_WINDOW", self._exit_pressed)

    def _exit_pressed(self):
        if self.frame_main.check_for_changes():
            if messagebox.askyesno(title="Promjene", message="Želite li spremite promjene?"):
                self.frame_main.save_changes()
                Changes.call_refresh_reminders()
        self.destroy()
